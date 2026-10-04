"""
Rice Disease Detector — Image Classification
Dataset: Archive 31 — 200 images (50 per class × 4 classes)
Classes: Bacterial Blight, Blast, Brown Spot, False Smut

Primary: TensorFlow/Keras MobileNetV2 transfer learning
Fallback: HOG + colour histogram features → SVM (if TF unavailable)
"""
import os
import pickle
from functools import lru_cache

IMG_DIR    = os.path.join(
    os.path.dirname(__file__), '..', '..', 'datasets',
    'archive (31)', 'Rice_Diseases'
)
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'rice_disease_model.pkl')
TF_PATH    = os.path.join(os.path.dirname(__file__), 'rice_disease_tf.keras')

CLASSES = {
    'Bacterial Blight Disease': {
        'display':     'Bacterial Blight',
        'color':       '#dc2626',
        'description': 'Causes yellowing and wilting of leaves from tips/margins. Leaves turn greyish-white.',
        'symptoms':    ['Yellow-white lesions on leaf edges', 'Leaves dry out from tips', 'Milky bacterial ooze visible'],
        'management':  'Use resistant varieties, apply copper-based bactericides, drain fields.',
        'severity':    'High',
        'icon':        'fa-biohazard',
    },
    'Blast Disease': {
        'display':     'Blast Disease',
        'color':       '#7c3aed',
        'description': 'Most devastating rice disease worldwide. Causes diamond-shaped lesions with grey centres.',
        'symptoms':    ['Diamond/eye-shaped spots on leaves', 'Grey-green water-soaked spots initially', 'Neck rot causes "white ear" — empty panicle'],
        'management':  'Fungicide (Tricyclazole), resistant varieties, balanced fertilization.',
        'severity':    'Critical',
        'icon':        'fa-skull-crossbones',
    },
    'Brown Spot Disease': {
        'display':     'Brown Spot',
        'color':       '#d97706',
        'description': 'Causes circular-to-oval brown spots with grey or whitish centres.',
        'symptoms':    ['Round-oval dark brown spots', 'Spots with lighter centre', 'Seed discoloration'],
        'management':  'Balanced NPK fertilization, fungicide (Iprodione), treat seeds before planting.',
        'severity':    'Medium',
        'icon':        'fa-circle-dot',
    },
    'False Smut Disease': {
        'display':     'False Smut',
        'color':       '#059669',
        'description': 'Individual grains replaced by velvety green/orange spore balls (false smut balls).',
        'symptoms':    ['Orange/green ball-like structures replacing grains', 'Reduced grain filling', 'Spore masses on panicle'],
        'management':  'Propiconazole fungicide at panicle emergence, avoid excessive nitrogen.',
        'severity':    'Medium',
        'icon':        'fa-circle',
    },
}

CLASS_DIRS = list(CLASSES.keys())


def _extract_features_pil(img_path, size=64):
    """Extract HOG-like + colour features using PIL only (no OpenCV)."""
    from PIL import Image
    import numpy as np

    img = Image.open(img_path).convert('RGB').resize((size, size))
    arr = np.array(img, dtype=np.float32) / 255.0

    # Colour histogram per channel (32 bins each)
    features = []
    for c in range(3):
        hist, _ = np.histogram(arr[:, :, c], bins=32, range=(0, 1))
        features.extend(hist / hist.sum())

    # Spatial colour means (4×4 grid)
    gs = size // 4
    for i in range(4):
        for j in range(4):
            patch = arr[i*gs:(i+1)*gs, j*gs:(j+1)*gs, :]
            features.extend(patch.mean(axis=(0, 1)).tolist())

    # Edge-like features via gradient magnitude
    grey = arr.mean(axis=2)
    gx = np.abs(np.diff(grey, axis=1)).mean()
    gy = np.abs(np.diff(grey, axis=0)).mean()
    features.extend([gx, gy])

    # Texture: LBP-approximation (std in patches)
    for i in range(4):
        for j in range(4):
            patch = grey[i*gs:(i+1)*gs, j*gs:(j+1)*gs]
            features.append(patch.std())

    return np.array(features, dtype=np.float32)


def _train_sklearn():
    """Train SVM on extracted features from the 200 images."""
    from sklearn.svm import SVC
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import accuracy_score, classification_report
    from sklearn.model_selection import cross_val_score
    import numpy as np

    print("Training rice disease detector (sklearn SVM on image features)...")
    X, y = [], []
    labels = []

    for cls_idx, cls_dir in enumerate(CLASS_DIRS):
        dir_path = os.path.join(IMG_DIR, cls_dir)
        if not os.path.isdir(dir_path):
            print(f"  WARNING: {dir_path} not found")
            continue
        imgs = [f for f in os.listdir(dir_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        print(f"  {cls_dir}: {len(imgs)} images")
        for img_file in imgs:
            try:
                feat = _extract_features_pil(os.path.join(dir_path, img_file))
                X.append(feat)
                y.append(cls_idx)
                labels.append(CLASS_DIRS[cls_idx])
            except Exception as e:
                print(f"    Skipping {img_file}: {e}")

    X = np.array(X)
    y = np.array(y)
    print(f"  Total samples: {len(X)}, feature dim: {X.shape[1]}")

    scaler = StandardScaler()
    X_sc   = scaler.fit_transform(X)

    # CV to estimate accuracy
    model  = SVC(kernel='rbf', C=10, gamma='scale', probability=True, random_state=42)
    cv_scores = cross_val_score(model, X_sc, y, cv=4, scoring='accuracy')
    print(f"  4-fold CV accuracy: {cv_scores.mean()*100:.1f}% ± {cv_scores.std()*100:.1f}%")

    # Fit final model
    model.fit(X_sc, y)
    train_acc = accuracy_score(y, model.predict(X_sc))
    print(f"  Train accuracy: {train_acc*100:.1f}%")

    bundle = {
        'backend': 'sklearn',
        'model':   model,
        'scaler':  scaler,
        'classes': CLASS_DIRS,
        'cv_acc':  round(float(cv_scores.mean()), 3),
    }
    return bundle


def _train_tensorflow():
    """Train MobileNetV2 transfer learning model."""
    import tensorflow as tf
    from tensorflow.keras import layers, Model
    from tensorflow.keras.applications import MobileNetV2
    from tensorflow.keras.preprocessing.image import ImageDataGenerator
    import numpy as np

    IMG_SIZE   = 160
    BATCH_SIZE = 16
    EPOCHS_FT  = 5
    EPOCHS_TL  = 10

    print("Training rice disease CNN (MobileNetV2 transfer learning)...")

    datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.1,
        height_shift_range=0.1,
        horizontal_flip=True,
        vertical_flip=True,
        brightness_range=[0.8, 1.2],
        zoom_range=0.15,
        validation_split=0.2,
    )

    train_gen = datagen.flow_from_directory(
        IMG_DIR,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='training',
        shuffle=True,
        seed=42,
    )
    val_gen = datagen.flow_from_directory(
        IMG_DIR,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='validation',
        seed=42,
    )

    n_classes = len(train_gen.class_indices)
    print(f"  Classes: {train_gen.class_indices}")

    # Build model
    base = MobileNetV2(
        input_shape=(IMG_SIZE, IMG_SIZE, 3),
        include_top=False,
        weights='imagenet',
    )
    base.trainable = False  # freeze base first

    inputs  = tf.keras.Input(shape=(IMG_SIZE, IMG_SIZE, 3))
    x       = base(inputs, training=False)
    x       = layers.GlobalAveragePooling2D()(x)
    x       = layers.Dropout(0.3)(x)
    x       = layers.Dense(128, activation='relu')(x)
    x       = layers.Dropout(0.2)(x)
    outputs = layers.Dense(n_classes, activation='softmax')(x)
    model   = Model(inputs, outputs)

    model.compile(
        optimizer=tf.keras.optimizers.Adam(1e-3),
        loss='categorical_crossentropy',
        metrics=['accuracy'],
    )

    # Phase 1: train head
    print("  Phase 1: training classification head...")
    model.fit(train_gen, validation_data=val_gen, epochs=EPOCHS_TL, verbose=0)

    # Phase 2: fine-tune last 20 layers of base
    base.trainable = True
    for layer in base.layers[:-20]:
        layer.trainable = False
    model.compile(
        optimizer=tf.keras.optimizers.Adam(1e-4),
        loss='categorical_crossentropy',
        metrics=['accuracy'],
    )
    print("  Phase 2: fine-tuning last 20 base layers...")
    model.fit(train_gen, validation_data=val_gen, epochs=EPOCHS_FT, verbose=0)

    val_loss, val_acc = model.evaluate(val_gen, verbose=0)
    print(f"  Val accuracy: {val_acc*100:.1f}%")

    # Save TF model
    model.save(TF_PATH)
    class_to_idx = train_gen.class_indices
    idx_to_class = {v: k for k, v in class_to_idx.items()}

    bundle = {
        'backend':      'tensorflow',
        'model_path':   TF_PATH,
        'idx_to_class': idx_to_class,
        'img_size':     IMG_SIZE,
        'val_acc':      round(float(val_acc), 3),
    }
    return bundle


def _train_and_save():
    """Try TensorFlow first, fall back to sklearn."""
    try:
        import tensorflow as tf
        print("TensorFlow found — using CNN approach")
        bundle = _train_tensorflow()
    except ImportError:
        print("TensorFlow not available — using sklearn feature extraction")
        bundle = _train_sklearn()

    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(bundle, f)
    print(f"  Saved bundle to {MODEL_PATH}")
    return bundle


@lru_cache(maxsize=1)
def load_rice_disease_bundle():
    if not os.path.exists(MODEL_PATH):
        return _train_and_save()
    with open(MODEL_PATH, 'rb') as f:
        bundle = pickle.load(f)
    # For TF backend, load model separately
    if bundle.get('backend') == 'tensorflow':
        try:
            import tensorflow as tf
            bundle['tf_model'] = tf.keras.models.load_model(bundle['model_path'])
        except Exception:
            bundle['backend'] = 'tf_load_failed'
    return bundle


def predict_rice_disease(image_file):
    """
    image_file: Django InMemoryUploadedFile or file path
    Returns: {disease, display, confidence, top3, info}
    """
    from PIL import Image
    import numpy as np

    bundle  = load_rice_disease_bundle()
    backend = bundle.get('backend', 'sklearn')

    # Load image
    if hasattr(image_file, 'read'):
        image_file.seek(0)
        img = Image.open(image_file).convert('RGB')
    else:
        img = Image.open(image_file).convert('RGB')

    if backend == 'tensorflow':
        img_size = bundle['img_size']
        img_arr  = np.array(img.resize((img_size, img_size)), dtype=np.float32) / 255.0
        img_arr  = np.expand_dims(img_arr, axis=0)
        proba    = bundle['tf_model'].predict(img_arr, verbose=0)[0]
        idx_to_class = bundle['idx_to_class']
        top_indices  = proba.argsort()[::-1][:3]
        top3 = []
        for i in top_indices:
            cls_dir = idx_to_class.get(int(i), '')
            info    = CLASSES.get(cls_dir, {'display': cls_dir})
            top3.append({
                'disease':    cls_dir,
                'display':    info.get('display', cls_dir),
                'confidence': round(float(proba[i]) * 100, 1),
                'info':       info,
            })
    else:
        # sklearn
        feat   = _extract_features_pil(img if hasattr(img, 'filename') else img)
        # Handle PIL Image directly
        if not isinstance(feat, np.ndarray):
            # Rebuild from PIL image
            img_arr = np.array(img.resize((64, 64)), dtype=np.float32) / 255.0
            feat = _extract_features_from_array(img_arr)
        scaler = bundle['scaler']
        model  = bundle['model']
        X      = scaler.transform([feat])
        proba  = model.predict_proba(X)[0]
        classes = bundle['classes']
        top_indices = proba.argsort()[::-1][:3]
        top3 = []
        for i in top_indices:
            cls_dir = classes[int(i)]
            info    = CLASSES.get(cls_dir, {'display': cls_dir})
            top3.append({
                'disease':    cls_dir,
                'display':    info.get('display', cls_dir),
                'confidence': round(float(proba[i]) * 100, 1),
                'info':       info,
            })

    top = top3[0] if top3 else {}
    return {
        'top_disease': top.get('disease', ''),
        'top_display': top.get('display', 'Unknown'),
        'confidence':  top.get('confidence', 0),
        'top3':        top3,
        'info':        top.get('info', {}),
        'backend':     backend,
    }


def _extract_features_from_array(arr):
    """Extract features from numpy array (64×64×3 float32)."""
    import numpy as np
    size = arr.shape[0]
    features = []

    # Colour histogram per channel
    for c in range(3):
        hist, _ = np.histogram(arr[:, :, c], bins=32, range=(0, 1))
        features.extend(hist / (hist.sum() + 1e-8))

    # Spatial colour means (4×4 grid)
    gs = size // 4
    for i in range(4):
        for j in range(4):
            patch = arr[i*gs:(i+1)*gs, j*gs:(j+1)*gs, :]
            features.extend(patch.mean(axis=(0, 1)).tolist())

    # Edge features
    grey = arr.mean(axis=2)
    gx = np.abs(np.diff(grey, axis=1)).mean()
    gy = np.abs(np.diff(grey, axis=0)).mean()
    features.extend([gx, gy])

    # Texture
    for i in range(4):
        for j in range(4):
            patch = grey[i*gs:(i+1)*gs, j*gs:(j+1)*gs]
            features.append(patch.std())

    return np.array(features, dtype=np.float32)


def predict_rice_disease_from_pil(pil_image):
    """Predict from an already-opened PIL Image."""
    import numpy as np

    bundle  = load_rice_disease_bundle()
    backend = bundle.get('backend', 'sklearn')

    if backend == 'tensorflow':
        img_size = bundle['img_size']
        img_arr  = np.array(pil_image.resize((img_size, img_size)).convert('RGB'),
                            dtype=np.float32) / 255.0
        img_arr  = np.expand_dims(img_arr, axis=0)
        proba    = bundle['tf_model'].predict(img_arr, verbose=0)[0]
        idx_to_class = bundle['idx_to_class']
        top_indices  = proba.argsort()[::-1][:3]
        top3 = []
        for i in top_indices:
            cls_dir = idx_to_class.get(int(i), '')
            info    = CLASSES.get(cls_dir, {'display': cls_dir})
            top3.append({
                'disease':    cls_dir,
                'display':    info.get('display', cls_dir),
                'confidence': round(float(proba[i]) * 100, 1),
                'info':       info,
            })
    else:
        arr    = np.array(pil_image.resize((64, 64)).convert('RGB'), dtype=np.float32) / 255.0
        feat   = _extract_features_from_array(arr)
        scaler = bundle['scaler']
        model  = bundle['model']
        X      = scaler.transform([feat])
        proba  = model.predict_proba(X)[0]
        classes = bundle['classes']
        top_indices = proba.argsort()[::-1][:3]
        top3 = []
        for i in top_indices:
            cls_dir = classes[int(i)]
            info    = CLASSES.get(cls_dir, {'display': cls_dir})
            top3.append({
                'disease':    cls_dir,
                'display':    info.get('display', cls_dir),
                'confidence': round(float(proba[i]) * 100, 1),
                'info':       info,
            })

    top = top3[0] if top3 else {}
    return {
        'top_disease': top.get('disease', ''),
        'top_display': top.get('display', 'Unknown'),
        'confidence':  top.get('confidence', 0),
        'top3':        top3,
        'info':        top.get('info', {}),
        'backend':     backend,
    }

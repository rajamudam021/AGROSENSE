"""
data.py - Comprehensive data module for Smart AI Farming Advisor
Contains crop data, market prices, soil health calculations, seasonal info,
fertilizer recommendations, and yield/profit estimations.
"""

import datetime

# ---------------------------------------------------------------------------
# CROP DATA
# ---------------------------------------------------------------------------

CROP_DATA = {
    'rice': {
        'fertilizer': {
            'N': 'Urea (120 kg/ha)',
            'P': 'Single Super Phosphate (60 kg/ha)',
            'K': 'Muriate of Potash (40 kg/ha)',
        },
        'irrigation': {
            'frequency': 'Every 3-5 days (keep 5 cm standing water during vegetative stage)',
            'notes': 'Drain field 2 weeks before harvest. Avoid water stress during flowering.',
        },
        'rotation': ['wheat', 'lentil', 'chickpea', 'mustard'],
        'season': 'Kharif',
        'yield_per_hectare': 4.5,
        'market_price': 2183,
        'timeline': [
            {'stage': 'Land Preparation', 'days': '0-7', 'desc': 'Plough field, puddle soil, level field for uniform water distribution.'},
            {'stage': 'Nursery / Sowing', 'days': '8-30', 'desc': 'Prepare nursery beds, sow pre-germinated seeds at 40 kg/ha.'},
            {'stage': 'Transplanting', 'days': '31-35', 'desc': 'Transplant 20-25 day old seedlings at 20x15 cm spacing.'},
            {'stage': 'Vegetative Growth', 'days': '36-75', 'desc': 'Apply basal dose fertilizer. Maintain 5 cm water level.'},
            {'stage': 'Panicle Initiation', 'days': '76-90', 'desc': 'Apply top-dressing nitrogen. Manage pests actively.'},
            {'stage': 'Flowering & Grain Fill', 'days': '91-110', 'desc': 'Ensure adequate water. Spray micronutrients if needed.'},
            {'stage': 'Maturity & Harvest', 'days': '111-120', 'desc': 'Drain field, harvest when 80% grains turn golden yellow.'},
        ],
        'tips': [
            'Use certified high-yielding varieties like IR-64, Swarna, or Pusa Basmati for better returns.',
            'Practice the System of Rice Intensification (SRI) to reduce seed usage by 80-90%.',
            'Apply zinc sulfate (25 kg/ha) as basal dose to prevent zinc deficiency common in rice soils.',
            'Use conoweeder for mechanical weeding to reduce herbicide costs and improve aeration.',
            'Monitor for brown plant hopper and stem borer - use neem-based pesticides as first line of defense.',
        ],
        'calendar': {
            'Jan': 'Land preparation for rabi; harvest late Kharif varieties',
            'Feb': 'Harvest remaining crop; soil testing',
            'Mar': 'Land preparation; procure seeds',
            'Apr': 'Irrigation scheduling; procure inputs',
            'May': 'Nursery preparation; apply FYM',
            'Jun': 'Sowing in nursery; land preparation',
            'Jul': 'Transplanting; first fertilizer dose',
            'Aug': 'Weeding; pest monitoring; top-dress nitrogen',
            'Sep': 'Panicle initiation; irrigation management',
            'Oct': 'Flowering; grain fill; water management',
            'Nov': 'Harvest; threshing',
            'Dec': 'Post-harvest tillage; straw management',
        },
    },

    'maize': {
        'fertilizer': {
            'N': 'Urea (150 kg/ha in split doses)',
            'P': 'Di-Ammonium Phosphate (75 kg/ha)',
            'K': 'Muriate of Potash (60 kg/ha)',
        },
        'irrigation': {
            'frequency': 'Every 7-10 days; critical at knee-high, tasseling, and silking stages',
            'notes': 'Avoid waterlogging. Drip or furrow irrigation preferred.',
        },
        'rotation': ['wheat', 'soybean', 'groundnut', 'chickpea'],
        'season': 'Kharif',
        'yield_per_hectare': 5.5,
        'market_price': 1870,
        'timeline': [
            {'stage': 'Land Preparation', 'days': '0-7', 'desc': 'Deep ploughing and harrowing. Apply FYM 10 t/ha.'},
            {'stage': 'Sowing', 'days': '8-10', 'desc': 'Sow seeds at 60x20 cm spacing, 4-5 cm depth. Seed rate 20 kg/ha.'},
            {'stage': 'Germination', 'days': '11-17', 'desc': 'Ensure soil moisture. Thin to one plant per hill after 15 days.'},
            {'stage': 'Vegetative (V-stage)', 'days': '18-45', 'desc': 'Apply 1/3rd N. Weed at 3-4 weeks. Earth up at 30 days.'},
            {'stage': 'Tasseling / Silking', 'days': '46-70', 'desc': 'Apply remaining N. Critical irrigation period. Hand pollination for seed crop.'},
            {'stage': 'Grain Fill', 'days': '71-90', 'desc': 'Monitor for stem borer. Ensure nutrition supply.'},
            {'stage': 'Harvest', 'days': '91-105', 'desc': 'Harvest when husks are dry and kernels show black layer.'},
        ],
        'tips': [
            'Use hybrid seeds (e.g., DKC 9144, Pioneer 30V92) for 30-40% higher yields.',
            'Apply boron (1.5 kg/ha) to improve pollination and grain set.',
            'Intercrop with soybean at 2:1 ratio to improve soil nitrogen and maximize income.',
            'Use fall armyworm pheromone traps - check fields twice weekly during V4-V8 stage.',
            'Ensure proper plant population of 55,000-60,000 plants/ha for optimal yields.',
        ],
        'calendar': {
            'Jan': 'Rabi maize harvest; land preparation',
            'Feb': 'Harvest and post-harvest storage',
            'Mar': 'Spring/summer maize sowing',
            'Apr': 'Fertilizer application; irrigation',
            'May': 'Harvest spring maize; prepare for Kharif',
            'Jun': 'Kharif sowing begins; land prep',
            'Jul': 'Thinning; weeding; fertilizer top-dress',
            'Aug': 'Pest monitoring; earth-up; irrigation',
            'Sep': 'Grain-fill stage; final fertilizer',
            'Oct': 'Harvest Kharif maize; drying',
            'Nov': 'Storage; rabi maize sowing (south India)',
            'Dec': 'Rabi maize vegetative growth; irrigation',
        },
    },

    'cotton': {
        'fertilizer': {
            'N': 'Urea (100-150 kg/ha in 3 splits)',
            'P': 'Single Super Phosphate (60 kg/ha basal)',
            'K': 'Muriate of Potash (100 kg/ha)',
        },
        'irrigation': {
            'frequency': 'Every 10-15 days; critical at squaring, flowering, and boll development',
            'notes': 'Avoid water stress during boll formation. Stop irrigation 3 weeks before harvest.',
        },
        'rotation': ['wheat', 'chickpea', 'sorghum', 'groundnut'],
        'season': 'Kharif',
        'yield_per_hectare': 2.0,
        'market_price': 6620,
        'timeline': [
            {'stage': 'Land Preparation', 'days': '0-10', 'desc': 'Deep ploughing (30 cm). Apply FYM 15-20 t/ha. Prepare ridges and furrows.'},
            {'stage': 'Sowing', 'days': '11-15', 'desc': 'Sow Bt cotton seeds at 90x60 cm spacing. Treat with Trichoderma.'},
            {'stage': 'Seedling Establishment', 'days': '16-40', 'desc': 'Gap filling at 15 days. First weeding at 20-25 days.'},
            {'stage': 'Squaring', 'days': '41-60', 'desc': 'Apply 1st split N. Monitor for jassids and thrips.'},
            {'stage': 'Flowering', 'days': '61-90', 'desc': 'Apply 2nd split N + K. Critical period for bollworm management.'},
            {'stage': 'Boll Development', 'days': '91-120', 'desc': 'Apply 3rd split N. Use pheromone traps for bollworm.'},
            {'stage': 'Boll Opening & Harvest', 'days': '121-180', 'desc': 'Harvest in 3-4 pickings when bolls open fully (80% open).'},
        ],
        'tips': [
            'Use Bt cotton hybrid varieties registered with the government for bollworm resistance.',
            'Maintain a refugia of 5% non-Bt cotton (e.g., 1 row per 20 rows) to delay resistance.',
            'Apply potassium humate to improve fibre quality and stress tolerance.',
            'Monitor 10 plants per acre weekly for bollworm egg laying using ETL-based approach.',
            'Foliar spray of 2% KNO3 at boll development stage improves boll retention.',
        ],
        'calendar': {
            'Jan': 'Late harvest; post-harvest soil management',
            'Feb': 'Stalks destruction; off-season tillage',
            'Mar': 'Deep ploughing; apply FYM',
            'Apr': 'Land preparation; procure seeds',
            'May': 'Early sowing in south India; irrigate',
            'Jun': 'Main sowing season; seed treatment',
            'Jul': 'Weeding; gap filling; apply basal fertilizer',
            'Aug': 'Squaring; pest scouting; first N split',
            'Sep': 'Flowering; second fertilizer dose',
            'Oct': 'Boll development; bollworm management',
            'Nov': 'First picking; apply top-dress',
            'Dec': 'Second/third picking; crop closure',
        },
    },

    'wheat': {
        'fertilizer': {
            'N': 'Urea (120 kg/ha in 3 splits)',
            'P': 'Di-Ammonium Phosphate (60 kg/ha basal)',
            'K': 'Muriate of Potash (40 kg/ha basal)',
        },
        'irrigation': {
            'frequency': 'At crown root initiation (21 days), tillering (40 days), jointing (60 days), flowering (80 days), grain fill (95 days)',
            'notes': '5-6 irrigations needed. Avoid waterlogging. Furrow irrigation recommended.',
        },
        'rotation': ['rice', 'cotton', 'soybean', 'sugarcane'],
        'season': 'Rabi',
        'yield_per_hectare': 4.8,
        'market_price': 2275,
        'timeline': [
            {'stage': 'Land Preparation', 'days': '0-7', 'desc': 'Fine seedbed preparation. Apply FYM 10 t/ha. Level field.'},
            {'stage': 'Sowing', 'days': '8-12', 'desc': 'Sow at 22.5 cm row spacing, 5 cm depth. Seed rate 100-125 kg/ha.'},
            {'stage': 'Crown Root Initiation', 'days': '13-25', 'desc': 'First irrigation. Apply 1/3rd N + full P + K.'},
            {'stage': 'Tillering', 'days': '26-50', 'desc': 'Second irrigation. Weed control. Apply 1/3rd N.'},
            {'stage': 'Jointing / Booting', 'days': '51-75', 'desc': 'Third irrigation. Apply last 1/3rd N. Monitor for rust.'},
            {'stage': 'Flowering / Grain Fill', 'days': '76-100', 'desc': 'Irrigation at flowering. Spray fungicide if rust observed.'},
            {'stage': 'Harvest', 'days': '101-120', 'desc': 'Harvest when moisture is 14-15%. Use combine harvester.'},
        ],
        'tips': [
            'Sow at optimum time (Nov 1-15 for north India) to avoid terminal heat stress.',
            'Use zero-till sowing after paddy harvest to save cost and conserve moisture.',
            'Apply sulfur (20 kg/ha) as basal to improve grain protein content.',
            'Spray propiconazole (0.1%) to manage yellow rust when first pustules appear.',
            'Use HD-2967, GW-322 or PBW-550 varieties for high yield under irrigated conditions.',
        ],
        'calendar': {
            'Jan': 'Irrigation; top-dress nitrogen; weed control',
            'Feb': 'Jointing stage; pest monitoring; irrigation',
            'Mar': 'Grain fill; irrigation; fungicide if needed',
            'Apr': 'Harvest; threshing; storage',
            'May': 'Storage management; market',
            'Jun': 'Land preparation for Kharif',
            'Jul': 'Kharif crop management',
            'Aug': 'Kharif crop management',
            'Sep': 'Kharif crop management',
            'Oct': 'Harvest Kharif; land prep for wheat',
            'Nov': 'Sowing season; apply basal fertilizer',
            'Dec': 'Crown root irrigation; early weed control',
        },
    },

    'chickpea': {
        'fertilizer': {
            'N': 'Urea (20 kg/ha basal only - N-fixing legume)',
            'P': 'Single Super Phosphate (80 kg/ha)',
            'K': 'Muriate of Potash (20 kg/ha)',
        },
        'irrigation': {
            'frequency': 'Pre-sowing irrigation + 1-2 protective irrigations at flowering and pod filling',
            'notes': 'Chickpea is drought-tolerant. Excess water causes root rot. Avoid waterlogging.',
        },
        'rotation': ['wheat', 'rice', 'cotton', 'sorghum'],
        'season': 'Rabi',
        'yield_per_hectare': 1.8,
        'market_price': 5400,
        'timeline': [
            {'stage': 'Land Preparation', 'days': '0-7', 'desc': 'Medium tilth. Add Rhizobium biofertilizer to seeds.'},
            {'stage': 'Sowing', 'days': '8-12', 'desc': 'Sow 30x10 cm spacing at 8-10 cm depth. Seed rate 80-100 kg/ha.'},
            {'stage': 'Vegetative Growth', 'days': '13-45', 'desc': 'One hand weeding at 25-30 days. Avoid excessive irrigation.'},
            {'stage': 'Flowering', 'days': '46-70', 'desc': 'Protective irrigation at flower initiation. Monitor for pod borer.'},
            {'stage': 'Pod Development', 'days': '71-90', 'desc': 'Apply pod borer management. Second protective irrigation.'},
            {'stage': 'Harvest', 'days': '91-110', 'desc': 'Harvest when plants yellow and 90% pods mature. Thresh immediately.'},
        ],
        'tips': [
            'Seed inoculation with Mesorhizobium ciceri Rhizobium can fix 60-70 kg N/ha reducing fertilizer need.',
            'Varieties like JG-11, Pusa-362 are tolerant to wilt and root rot.',
            'Use T-shaped bird perches (10/acre) to attract natural predators of pod borer.',
            'Spray 5% NSKE or HaNPV (200 LE/ha) for pod borer management as first option.',
            'Avoid excessive vegetative growth - use growth regulators like CCC if necessary.',
        ],
        'calendar': {
            'Jan': 'Pod development; protective irrigation',
            'Feb': 'Harvest; threshing; storage',
            'Mar': 'Market; storage management',
            'Apr': 'Procure seeds for next season',
            'May': 'Off-season land preparation',
            'Jun': 'Deep ploughing; incorporate FYM',
            'Jul': 'Land preparation; rabi planning',
            'Aug': 'Procure inputs; soil testing',
            'Sep': 'Pre-sowing irrigation; land prep',
            'Oct': 'Sowing season (Oct 15-Nov 15)',
            'Nov': 'Weeding; first vegetative growth',
            'Dec': 'Flowering; pod borer monitoring',
        },
    },

    'banana': {
        'fertilizer': {
            'N': 'Urea (200 g/plant/year in quarterly splits)',
            'P': 'Single Super Phosphate (70 g/plant/year)',
            'K': 'Muriate of Potash (300 g/plant/year - critical)',
        },
        'irrigation': {
            'frequency': 'Every 3-4 days in summer; 7-10 days in winter via drip/basin irrigation',
            'notes': 'Banana is highly sensitive to water stress. Drip irrigation saves 40-50% water.',
        },
        'rotation': ['legumes (intercrop)', 'groundnut', 'cowpea'],
        'season': 'Perennial',
        'yield_per_hectare': 35.0,
        'market_price': 1500,
        'timeline': [
            {'stage': 'Field Preparation & Planting', 'days': '0-15', 'desc': 'Dig pits 60x60x60 cm. Plant tissue culture or sword suckers.'},
            {'stage': 'Establishment', 'days': '16-60', 'desc': 'Irrigation every 2-3 days. Apply first fertilizer dose at 45 days.'},
            {'stage': 'Vegetative Growth', 'days': '61-150', 'desc': 'Monthly fertilizer. Weed management. Desuckering - keep one follower.'},
            {'stage': 'Shooting / Inflorescence', 'days': '151-210', 'desc': 'Prop plants with bamboo poles. Remove male bud after last hand develops.'},
            {'stage': 'Bunch Development', 'days': '211-280', 'desc': 'Cover bunch with perforated polythene bag. Apply K fertilizer.'},
            {'stage': 'Harvest', 'days': '281-365', 'desc': 'Harvest when upper surface of fingers flatten (3/4 maturity).'},
        ],
        'tips': [
            'Use tissue culture plants for disease-free, uniform crop and 20-25% higher yield.',
            'Practice "leaf pruning" - remove old and dried leaves to prevent diseases.',
            'Bunch covering with blue/silver polyethylene bags improves fruit quality and color.',
            'Apply micronutrients (Mg, Zn, Fe) foliar spray for correction of deficiencies.',
            'Rat management is critical - use bait stations and keep field clean.',
        ],
        'calendar': {
            'Jan': 'Harvest; plant new suckers; fertilize',
            'Feb': 'Bunch bagging; irrigation management',
            'Mar': 'Fertilizer application; pest scouting',
            'Apr': 'Irrigation critical; mulching',
            'May': 'Summer irrigation management; weeding',
            'Jun': 'Rainfall management; drainage',
            'Jul': 'Fertilizer application; drainage',
            'Aug': 'Bunch emergence; propping',
            'Sep': 'Bunch development; male bud removal',
            'Oct': 'Harvest; market',
            'Nov': 'Post-harvest management; new planting',
            'Dec': 'Winter irrigation; fertilize',
        },
    },

    'mango': {
        'fertilizer': {
            'N': 'Urea (1 kg/tree/year in splits)',
            'P': 'Single Super Phosphate (0.5 kg/tree/year)',
            'K': 'Muriate of Potash (1 kg/tree/year)',
        },
        'irrigation': {
            'frequency': 'Weekly during summer flowering (Jan-Mar); cease during monsoon; resume Oct-Dec',
            'notes': 'Irrigation stress during July-September promotes flowering next season.',
        },
        'rotation': ['groundnut (intercrop)', 'legumes', 'vegetables (young orchards)'],
        'season': 'Perennial',
        'yield_per_hectare': 10.0,
        'market_price': 4000,
        'timeline': [
            {'stage': 'Planting / Establishment', 'days': '0-365', 'desc': 'Plant grafted seedlings in pits 1x1x1m. Stake young trees.'},
            {'stage': 'Juvenile Phase', 'days': '366-1095', 'desc': '2-3 years vegetative growth. Formative pruning for shape.'},
            {'stage': 'First Flowering (Year 3-4)', 'days': '1096-1460', 'desc': 'Flower initiation in cool dry months (Oct-Nov). Apply P and K.'},
            {'stage': 'Fruit Development', 'days': '1461-1550', 'desc': 'Thin excess fruits. Apply foliar micronutrients.'},
            {'stage': 'Harvest', 'days': '1551-1600', 'desc': 'Harvest at physiological maturity (Apr-Jun for most varieties).'},
        ],
        'tips': [
            'Apply paclobutrazol (4-5 g a.i./tree) soil drench in Oct-Nov for early and assured flowering.',
            'Use "Mango Malformation" management: prune affected parts and apply NAA spray.',
            'Intercrop with legumes (groundnut, cowpea) in young orchards to generate income.',
            'Spray Bordeaux mixture (1%) during monsoon to prevent anthracnose and powdery mildew.',
            'Harvest with stalk attached to prevent sap burn which causes skin browning.',
        ],
        'calendar': {
            'Jan': 'Flowering; irrigation; frost protection',
            'Feb': 'Fruit set; insect pollination management',
            'Mar': 'Fruitlet thinning; fertilizer application',
            'Apr': 'Fruit development; pest monitoring',
            'May': 'Early harvest; market',
            'Jun': 'Main harvest; post-harvest treatment',
            'Jul': 'Post-harvest pruning; Bordeaux mixture',
            'Aug': 'Pruning; weed management; fertilize',
            'Sep': 'Vegetative flush; fertilizer',
            'Oct': 'Stress induction (stop irrigation)',
            'Nov': 'Paclobutrazol application if needed',
            'Dec': 'Flower bud differentiation; light irrigation',
        },
    },

    'grapes': {
        'fertilizer': {
            'N': 'Urea (500 g/vine/year in 4 splits)',
            'P': 'Single Super Phosphate (250 g/vine/year)',
            'K': 'Muriate of Potash (500 g/vine/year)',
        },
        'irrigation': {
            'frequency': 'Drip irrigation: 2-4 liters/vine/day; increase to 8-10L during berry development',
            'notes': 'Precise irrigation scheduling critical. Use tensiometer for soil moisture monitoring.',
        },
        'rotation': ['vegetables (intercrop in early years)', 'legumes'],
        'season': 'Perennial',
        'yield_per_hectare': 20.0,
        'market_price': 5000,
        'timeline': [
            {'stage': 'Pruning (Cane/Spur)', 'days': '0-7', 'desc': 'Annual pruning done Jan-Feb. Leave 4-8 buds per cane.'},
            {'stage': 'Bud Break & Shoot Growth', 'days': '8-30', 'desc': 'Apply nitrogen. Thin shoots. Shoot positioning on trellis.'},
            {'stage': 'Flowering', 'days': '31-60', 'desc': 'Minimal irrigation. Apply GA3 for berry size. Flower thinning.'},
            {'stage': 'Berry Set & Development', 'days': '61-100', 'desc': 'Increase irrigation. Bunch thinning. Apply boron, zinc sprays.'},
            {'stage': 'Veraison (color change)', 'days': '101-120', 'desc': 'Apply potassium. Leaf removal for sunlight exposure.'},
            {'stage': 'Harvest', 'days': '121-140', 'desc': 'Harvest when Brix > 16 for table grapes (India). Use sharp scissors.'},
        ],
        'tips': [
            'Apply GA3 (10-40 ppm) during full bloom to improve berry size in seedless varieties.',
            'Bordeaux mixture or Mancozeb (2.5 g/L) is essential for downy mildew management.',
            'Training on GDC (Geneva Double Curtain) or Bower system for high density planting.',
            'Post-harvest sulfur dioxide fumigation extends shelf life for export quality grapes.',
            'Cluster thinning (remove 30-40% clusters) improves remaining cluster quality and size.',
        ],
        'calendar': {
            'Jan': 'Pruning; apply basal fertilizer',
            'Feb': 'Bud break; shoot thinning',
            'Mar': 'Flowering; GA3 application; minimal irrigation',
            'Apr': 'Berry development; fungicide sprays',
            'May': 'Berry growth; bunch management',
            'Jun': 'Pre-harvest; irrigation reduction',
            'Jul': 'Harvest (Nashik/Thompson Seedless)',
            'Aug': 'Post-harvest pruning (October pruning prep)',
            'Sep': 'Second pruning (October variety)',
            'Oct': 'Bud break post-second pruning',
            'Nov': 'Flowering; fruit set management',
            'Dec': 'Berry development; winter management',
        },
    },

    'watermelon': {
        'fertilizer': {
            'N': 'Urea (80 kg/ha in 3 splits)',
            'P': 'Single Super Phosphate (40 kg/ha basal)',
            'K': 'Muriate of Potash (80 kg/ha)',
        },
        'irrigation': {
            'frequency': 'Drip: daily 30-40 mm; Basin: every 4-5 days. Reduce at fruit maturity.',
            'notes': 'Avoid irrigation 1 week before harvest - improves sugar content and reduces cracking.',
        },
        'rotation': ['wheat', 'maize', 'sorghum', 'legumes'],
        'season': 'Zaid',
        'yield_per_hectare': 30.0,
        'market_price': 600,
        'timeline': [
            {'stage': 'Land Prep & Pit Preparation', 'days': '0-7', 'desc': 'Prepare raised beds. Dig pits 60x60x45 cm at 2x3m spacing. Add compost.'},
            {'stage': 'Sowing', 'days': '8-12', 'desc': 'Sow 3-4 seeds per pit (2-3 cm depth). Thin to 2 seedlings at 10 days.'},
            {'stage': 'Vine Growth', 'days': '13-40', 'desc': 'Train vines. Apply first fertilizer. Weed between rows.'},
            {'stage': 'Flowering', 'days': '41-55', 'desc': 'Hand pollination if bee activity low. Apply K fertilizer.'},
            {'stage': 'Fruit Development', 'days': '56-80', 'desc': 'Place straw under fruits to prevent rotting. Foliar spray micronutrients.'},
            {'stage': 'Harvest', 'days': '81-90', 'desc': 'Harvest when fruit turns dull, tendril near fruit dries, and gives hollow sound on tapping.'},
        ],
        'tips': [
            'Use grafted watermelon on bottle gourd rootstock to avoid soil-borne diseases.',
            'Place beehives (2-4 per acre) to improve pollination and fruit set.',
            'Mulching with black LDPE mulch controls weeds and maintains soil moisture.',
            'Apply 1% calcium nitrate spray during fruit development to prevent blossom-end rot.',
            'Select seedless varieties (e.g., Madura) or seeded high-sugar varieties (Sugar Baby, Arka Manik).',
        ],
        'calendar': {
            'Jan': 'Not suitable (cold)',
            'Feb': 'Land preparation; procure seeds',
            'Mar': 'Sowing (Zaid season starts)',
            'Apr': 'Vine growth; fertilizer; irrigation',
            'May': 'Flowering; fruit development; harvest early',
            'Jun': 'Main harvest; market',
            'Jul': 'Off-season; land prep',
            'Aug': 'Not recommended (heavy rains)',
            'Sep': 'Not recommended',
            'Oct': 'Prepare for winter crop (south India)',
            'Nov': 'Winter/late crop in south India',
            'Dec': 'Not recommended (north India - cold)',
        },
    },

    'groundnut': {
        'fertilizer': {
            'N': 'Urea (20 kg/ha basal - legume)',
            'P': 'Single Super Phosphate (60 kg/ha)',
            'K': 'Muriate of Potash (40 kg/ha)',
        },
        'irrigation': {
            'frequency': 'Every 7-10 days; critical at pegging (40-45 days) and pod fill (70-90 days)',
            'notes': 'Total 4-5 irrigations needed. Avoid excess water - causes pod rot.',
        },
        'rotation': ['cotton', 'maize', 'rice', 'sorghum'],
        'season': 'Kharif',
        'yield_per_hectare': 2.5,
        'market_price': 5800,
        'timeline': [
            {'stage': 'Land Preparation', 'days': '0-7', 'desc': 'Deep ploughing. Gypsum 400 kg/ha as basal. Add FYM 5t/ha.'},
            {'stage': 'Sowing', 'days': '8-12', 'desc': 'Shell seeds. Treat with Trichoderma + Rhizobium. Row spacing 30x10 cm.'},
            {'stage': 'Vegetative Growth', 'days': '13-35', 'desc': 'Weed at 20-25 days. Earth up at 30 days to facilitate pegging.'},
            {'stage': 'Flowering & Pegging', 'days': '36-50', 'desc': 'Irrigate. Apply gypsum (200 kg/ha) during pegging for pod fill.'},
            {'stage': 'Pod Development', 'days': '51-90', 'desc': 'Foliar spray of micronutrients. Continue irrigation.'},
            {'stage': 'Harvest', 'days': '91-110', 'desc': 'Harvest when inner pod shell shows dark markings and leaves yellow.'},
        ],
        'tips': [
            'Seed inoculation with Bradyrhizobium inoculant can add 40-50 kg N/ha equivalence.',
            'Gypsum application at pegging stage is critical - provides calcium directly to pods.',
            'Use TMVGH or JL-24 varieties for high yield and oil content under Kharif conditions.',
            'Monitor for leaf miner and Tikka disease (early and late leaf spot) - spray Mancozeb.',
            'Windrow harvested plants for 1-2 weeks before threshing to reduce aflatoxin risk.',
        ],
        'calendar': {
            'Jan': 'Rabi groundnut harvesting; threshing',
            'Feb': 'Storage; market; land preparation',
            'Mar': 'Rabi groundnut sowing (south India)',
            'Apr': 'Summer crop management',
            'May': 'Summer harvest; kharif preparation',
            'Jun': 'Kharif sowing (June 15 - July 15)',
            'Jul': 'Weeding; earth-up; fertilizer',
            'Aug': 'Pegging; gypsum application',
            'Sep': 'Pod development; irrigation',
            'Oct': 'Harvest Kharif groundnut',
            'Nov': 'Threshing; storage; post-harvest',
            'Dec': 'Rabi groundnut sowing (if applicable)',
        },
    },

    'jute': {
        'fertilizer': {
            'N': 'Urea (100 kg/ha in 3 splits)',
            'P': 'Single Super Phosphate (30 kg/ha)',
            'K': 'Muriate of Potash (30 kg/ha)',
        },
        'irrigation': {
            'frequency': 'Largely rainfed. 1-2 irrigations during dry spells if needed.',
            'notes': 'Adequate soil moisture is critical in early growth. Avoid waterlogging.',
        },
        'rotation': ['rice', 'wheat', 'mustard', 'vegetables'],
        'season': 'Kharif',
        'yield_per_hectare': 2.8,
        'market_price': 4300,
        'timeline': [
            {'stage': 'Land Preparation', 'days': '0-7', 'desc': 'Fine seedbed preparation. Apply lime if pH < 6.0.'},
            {'stage': 'Sowing', 'days': '8-12', 'desc': 'Broadcast or line sowing. Seed rate 7-8 kg/ha. Sow March-April.'},
            {'stage': 'Thinning & Weeding', 'days': '13-35', 'desc': 'Thin to 7 cm spacing at 20-25 days. One weeding at 35 days.'},
            {'stage': 'Vegetative Growth', 'days': '36-80', 'desc': 'Apply N top-dressing in 2 splits. Monitor stem rot.'},
            {'stage': 'Flowering', 'days': '81-100', 'desc': 'Fiber development concurrent with flowering. Apply final N.'},
            {'stage': 'Harvest & Retting', 'days': '101-120', 'desc': 'Harvest at early flowering stage (before pods form). Ret in water 15-20 days.'},
        ],
        'tips': [
            'Harvest at 50% flowering for best fibre quality - do not wait for seed set.',
            'Use water retting in running water for bright, high-grade fibre.',
            'Bio-retting using Aspergillus and Bacillus cultures reduces retting time by 30%.',
            'JRO-524, JRO-632 are popular high-yielding white jute varieties.',
            'Add lime to acidic soils (pH < 5.5) to improve nutrient availability.',
        ],
        'calendar': {
            'Jan': 'Off-season; procure seeds',
            'Feb': 'Land preparation; procure seeds',
            'Mar': 'Early sowing (March 15-April 15)',
            'Apr': 'Main sowing; weeding; thinning',
            'May': 'Vegetative growth; fertilizer application',
            'Jun': 'Irrigation if dry; fertilizer top-dress',
            'Jul': 'Growth monitoring; pest management',
            'Aug': 'Flowering; pre-harvest preparation',
            'Sep': 'Harvest; retting',
            'Oct': 'Fibre extraction; drying; market',
            'Nov': 'Post-harvest; land preparation',
            'Dec': 'Off-season preparation',
        },
    },

    'coffee': {
        'fertilizer': {
            'N': 'Urea (250 g/plant/year in 3 splits)',
            'P': 'Rock Phosphate / SSP (125 g/plant/year)',
            'K': 'Muriate of Potash (250 g/plant/year)',
        },
        'irrigation': {
            'frequency': 'Sprinkler/drip irrigation weekly during dry months (Jan-Mar, May-Jun)',
            'notes': 'Irrigation during flowering initiation (blossom showers) is critical for yield.',
        },
        'rotation': ['pepper (intercrop)', 'cardamom', 'banana (shade tree)'],
        'season': 'Perennial',
        'yield_per_hectare': 1.5,
        'market_price': 18000,
        'timeline': [
            {'stage': 'Planting', 'days': '0-30', 'desc': 'Plant 1-year-old seedlings in pits 45x45x45 cm at 2.7x2.7 m spacing.'},
            {'stage': 'Establishment (Year 1-2)', 'days': '31-730', 'desc': 'Regular irrigation. Weed control. Formative pruning.'},
            {'stage': 'First Bearing (Year 3-4)', 'days': '731-1460', 'desc': 'First crop. Blossom showers critical. Apply full fertilizer.'},
            {'stage': 'Full Bearing', 'days': '1461+', 'desc': 'Full production. Annual skiffing/stumping pruning. Shade management.'},
            {'stage': 'Flowering & Berry Development', 'days': 'Annual', 'desc': 'Flowers appear Jan-Feb after blossom showers. Berries ripen Oct-Feb.'},
            {'stage': 'Harvest', 'days': 'Oct-Feb', 'desc': 'Selective picking (red cherries only) for Arabica; strip picking for Robusta.'},
        ],
        'tips': [
            'Maintain 40-50% shade cover with silver oak or Grevillea shade trees.',
            'Selective picking (red ripe cherries only) fetches premium prices in specialty coffee market.',
            'Apply bordeaux mixture (1%) after monsoon cessation to manage black rot and cercospora.',
            'Composting spent coffee pulp returns nutrients and improves soil organic matter.',
            'Annual soil testing and foliar analysis ensures precise fertilizer management in coffee.',
        ],
        'calendar': {
            'Jan': 'Harvest (Arabica); apply fertilizer post-harvest',
            'Feb': 'Harvest; blossom shower irrigation; pruning',
            'Mar': 'Berry development starts; irrigation',
            'Apr': 'Berry development; shade management',
            'May': 'Pre-monsoon shower flush; fertilizer',
            'Jun': 'Monsoon; drainage management; weed control',
            'Jul': 'Monsoon management; pest monitoring',
            'Aug': 'Berry development; fungicide application',
            'Sep': 'Pre-harvest preparation; fertilizer',
            'Oct': 'Harvest begins (Robusta); market',
            'Nov': 'Main harvest season; processing',
            'Dec': 'Harvest; drying; storage; market',
        },
    },

    'coconut': {
        'fertilizer': {
            'N': 'Urea (500 g/palm/year)',
            'P': 'Rock Phosphate / SSP (320 g/palm/year)',
            'K': 'Muriate of Potash (1200 g/palm/year - most critical)',
        },
        'irrigation': {
            'frequency': 'Basin/drip irrigation every 7-10 days in summer; 15-20 days in winter',
            'notes': 'Coconut responds well to drip irrigation. 40-45 liters/palm/day in peak summer.',
        },
        'rotation': ['cacao (intercrop)', 'banana', 'pineapple', 'pepper (intercrop)'],
        'season': 'Perennial',
        'yield_per_hectare': 11000.0,
        'market_price': 2800,
        'timeline': [
            {'stage': 'Planting', 'days': '0-30', 'desc': 'Plant 9-12 month old seedlings in 1x1x1 m pits at 7.5x7.5 m spacing.'},
            {'stage': 'Establishment (Yr 1-4)', 'days': '31-1460', 'desc': 'Mulch basin. Regular irrigation. Weed management. Fertilize annually.'},
            {'stage': 'First Bearing (Yr 5-7)', 'days': '1461-2555', 'desc': 'First nuts appear. Increase fertilizer. Monitor for rhinoceros beetle.'},
            {'stage': 'Full Bearing', 'days': '2556+', 'desc': '80-100 nuts/palm/year at full production. Harvest every 45 days.'},
            {'stage': 'Annual Harvest Cycle', 'days': 'Continuous', 'desc': 'Climb and harvest bunches every 45 days throughout year.'},
        ],
        'tips': [
            'Apply 2 kg wood ash or 1.5 kg MOP per palm - coconut is a heavy potassium feeder.',
            'Use green manure intercropping (Calapogonium) to improve soil organic matter.',
            'Rhinoceros beetle management: use pheromone traps and fill decayed stem wounds.',
            'Root feeding with 10:8:10 NPK solution during summer for quick nutrient uptake.',
            'Tall variety palms (West Coast Tall) more drought-tolerant; use hybrids for higher yield.',
        ],
        'calendar': {
            'Jan': 'Apply fertilizer (1st dose); harvest',
            'Feb': 'Irrigation; harvest; pest monitoring',
            'Mar': 'Summer irrigation begins; mulch',
            'Apr': 'Peak summer irrigation; fertilizer',
            'May': 'Pre-monsoon fertilizer application',
            'Jun': 'Monsoon; drainage; fertilize (2nd dose)',
            'Jul': 'Weed management; drainage',
            'Aug': 'Pest monitoring; harvest',
            'Sep': 'Post-monsoon fertilizer (3rd dose)',
            'Oct': 'Harvest; husk composting',
            'Nov': 'Harvest; soil management',
            'Dec': 'Harvest; annual assessment; planning',
        },
    },

    'papaya': {
        'fertilizer': {
            'N': 'Urea (200 g/plant/year in monthly doses)',
            'P': 'Single Super Phosphate (100 g/plant/year)',
            'K': 'Muriate of Potash (200 g/plant/year)',
        },
        'irrigation': {
            'frequency': 'Every 5-7 days. Drip irrigation 4-6 liters/plant/day.',
            'notes': 'Papaya is sensitive to both waterlogging and drought. Use raised beds.',
        },
        'rotation': ['legumes', 'maize', 'vegetables'],
        'season': 'Kharif',
        'yield_per_hectare': 40.0,
        'market_price': 1200,
        'timeline': [
            {'stage': 'Nursery', 'days': '0-30', 'desc': 'Raise seedlings in polybags. Sow 2-3 seeds per bag. Thin to 1 plant.'},
            {'stage': 'Field Planting', 'days': '31-45', 'desc': 'Plant in pits 2x2x0.5m. Plant 3 plants per pit initially (2 female, 1 male).'},
            {'stage': 'Establishment', 'days': '46-90', 'desc': 'Regular irrigation. First fertilizer at 30 days after transplanting.'},
            {'stage': 'Sex Determination & Thinning', 'days': '91-120', 'desc': 'Identify sex at first flowering. Retain 1-2 females per hill.'},
            {'stage': 'Fruit Development', 'days': '121-240', 'desc': 'Monthly fertilizer. Prop plants. Paper bag fruits for borer protection.'},
            {'stage': 'Harvest', 'days': '241-365', 'desc': 'Harvest when fruits show yellow streaks. Yield continuous for 2-3 years.'},
        ],
        'tips': [
            'Use hermaphrodite (bisexual) varieties like Red Lady or Pusa Dwarf to avoid sexing problem.',
            'Papaya ringspot virus is the major constraint - use virus-free seedlings and aphid control.',
            'Plastic mulch reduces weed growth and conserves moisture significantly.',
            'Apply 2% potassium nitrate foliar spray during fruit development to improve quality.',
            'Avoid transplanting in June-July monsoon to prevent damping-off in nursery.',
        ],
        'calendar': {
            'Jan': 'Harvest; fertilize; pest monitoring',
            'Feb': 'Harvest; irrigation management',
            'Mar': 'Summer irrigation; fruit thinning',
            'Apr': 'Peak summer management; mulch',
            'May': 'New nursery preparation; harvest',
            'Jun': 'Avoid transplanting; drainage',
            'Jul': 'Transplanting (raised beds); establish',
            'Aug': 'Vegetative growth; weed management',
            'Sep': 'Flowering; sex determination',
            'Oct': 'Fruit set; fertilize; prop',
            'Nov': 'Fruit development; harvest begins',
            'Dec': 'Harvest; market; fertilize',
        },
    },

    'orange': {
        'fertilizer': {
            'N': 'Urea (1 kg/tree/year in 3 splits)',
            'P': 'Single Super Phosphate (500 g/tree/year)',
            'K': 'Muriate of Potash (1 kg/tree/year)',
        },
        'irrigation': {
            'frequency': 'Weekly during fruit development; fortnightly at other times',
            'notes': 'Water stress during flowering is beneficial (promotes uniform flowering).',
        },
        'rotation': ['legumes (intercrop)', 'vegetables (young orchard)'],
        'season': 'Rabi',
        'yield_per_hectare': 12.0,
        'market_price': 3500,
        'timeline': [
            {'stage': 'Planting', 'days': '0-30', 'desc': 'Plant budded plants in 75x75x75 cm pits at 6x6 m spacing.'},
            {'stage': 'Establishment (Yr 1-3)', 'days': '31-1095', 'desc': 'Regular irrigation, weed management, formative pruning.'},
            {'stage': 'First Flowering (Yr 3-4)', 'days': '1096-1460', 'desc': 'First crop. Apply full fertilizer. Thin excess fruits.'},
            {'stage': 'Fruit Development', 'days': '1461-1550', 'desc': 'Foliar zinc and iron to prevent deficiencies. Irrigation critical.'},
            {'stage': 'Harvest', 'days': 'Nov-Jan', 'desc': 'Harvest when fruits develop full color. Clip-and-carry harvest method.'},
        ],
        'tips': [
            'Withhold irrigation for 4-6 weeks after September to induce uniform flowering.',
            'Zinc deficiency (little leaf) is common in Nagpur oranges - spray 0.5% ZnSO4.',
            'Tristeza virus is the most important disease - use certified virus-indexed planting material.',
            'Micronutrient spray (0.5% ZnSO4 + 0.3% FeSO4 + 0.2% MnSO4) improves fruit quality.',
            'Apply 50 kg FYM or compost per tree annually to maintain soil organic matter.',
        ],
        'calendar': {
            'Jan': 'Harvest; market; post-harvest care',
            'Feb': 'Pruning; apply basal fertilizer',
            'Mar': 'Water stress period (stop irrigation)',
            'Apr': 'Flowering (ambia bahar); irrigation resumes',
            'May': 'Fruit set; thin excess fruits',
            'Jun': 'Monsoon begins; drainage management',
            'Jul': 'Fruit development; pest monitoring',
            'Aug': 'Fertilizer application; weed management',
            'Sep': 'Fruit sizing; foliar micronutrients',
            'Oct': 'Pre-harvest; stop excess irrigation',
            'Nov': 'Harvest begins; market',
            'Dec': 'Main harvest season; storage',
        },
    },

    'apple': {
        'fertilizer': {
            'N': 'Urea (500 g/tree/year for young trees; 1 kg for bearing trees)',
            'P': 'Single Super Phosphate (300 g/tree/year)',
            'K': 'Muriate of Potash (500 g/tree/year)',
        },
        'irrigation': {
            'frequency': 'Weekly during fruit development; rainfed in Himachal/J&K mostly',
            'notes': 'Water stress at pink bud stage and fruit set is critical to avoid. Micro-sprinkler irrigation effective.',
        },
        'rotation': ['vegetables (between rows of young orchards)'],
        'season': 'Rabi',
        'yield_per_hectare': 20.0,
        'market_price': 7000,
        'timeline': [
            {'stage': 'Dormancy & Pruning', 'days': 'Dec-Feb', 'desc': 'Annual pruning during dormancy. Apply copper fungicide to pruning cuts.'},
            {'stage': 'Bud Break', 'days': 'Mar', 'desc': 'Apply fertilizer. Spray lime sulfur for overwintering pests.'},
            {'stage': 'Flowering', 'days': 'Apr-May', 'desc': 'Place beehives for pollination. No pesticide spray during bloom.'},
            {'stage': 'Fruit Set & June Drop', 'days': 'May-Jun', 'desc': 'Thin fruits to 1 per spur. Apply calcium spray to prevent bitterpit.'},
            {'stage': 'Fruit Development', 'days': 'Jun-Sep', 'desc': 'Calcium sprays (4-6 times). Codling moth management.'},
            {'stage': 'Harvest', 'days': 'Sep-Oct', 'desc': 'Harvest based on starch-iodine test and firmness. Cool store immediately.'},
        ],
        'tips': [
            'Require 1000-1500 chilling hours (below 7.2°C) - choose varieties based on local chilling.',
            'Low chill varieties (HRMN-99, Anna) suited for lower altitudes and warmer climates.',
            'Thinning is critical - leave 1 fruit per 20-25 leaves for large fruit size.',
            'Reflective mulch (metalized polyethylene) improves red coloration in Royal Delicious.',
            'Bitter pit (calcium deficiency) prevented by 0.6% CaCl2 sprays starting after petal fall.',
        ],
        'calendar': {
            'Jan': 'Dormancy; pruning; dormant spray',
            'Feb': 'Pruning completion; fertilizer application',
            'Mar': 'Bud break; lime sulfur spray',
            'Apr': 'Flowering; bee placement; no pesticide',
            'May': 'Fruit set; thinning; calcium spray',
            'Jun': 'June drop; fruit thinning; irrigation',
            'Jul': 'Fruit development; codling moth spray',
            'Aug': 'Fruit sizing; calcium sprays',
            'Sep': 'Pre-harvest; color development',
            'Oct': 'Main harvest; cool storage',
            'Nov': 'Post-harvest; soil management',
            'Dec': 'Dormancy; planning; pruning begins',
        },
    },

    'lentil': {
        'fertilizer': {
            'N': 'Urea (20 kg/ha basal - legume, minimal N)',
            'P': 'Single Super Phosphate (60 kg/ha)',
            'K': 'Muriate of Potash (20 kg/ha)',
        },
        'irrigation': {
            'frequency': 'Pre-sowing + 1-2 protective irrigations at branching (30-35 days) and pod fill (65-70 days)',
            'notes': 'Lentil is a drought-tolerant Rabi crop. Excess moisture causes disease.',
        },
        'rotation': ['wheat', 'rice', 'maize', 'cotton'],
        'season': 'Rabi',
        'yield_per_hectare': 1.2,
        'market_price': 5500,
        'timeline': [
            {'stage': 'Land Preparation', 'days': '0-7', 'desc': 'Fine seedbed. Apply Rhizobium inoculant to seeds.'},
            {'stage': 'Sowing', 'days': '8-12', 'desc': 'Sow Oct-Nov at 25x5 cm. Seed rate 40-50 kg/ha.'},
            {'stage': 'Vegetative Growth', 'days': '13-40', 'desc': 'One weeding at 25-30 days. Apply P and K basal.'},
            {'stage': 'Flowering', 'days': '41-65', 'desc': 'Protective irrigation if dry. Monitor for aphids and wilt.'},
            {'stage': 'Pod Fill', 'days': '66-90', 'desc': 'Second protective irrigation. Watch for rust.'},
            {'stage': 'Harvest', 'days': '91-110', 'desc': 'Harvest when lower pods turn brown. Windrow before threshing.'},
        ],
        'tips': [
            'Seed inoculation with Rhizobium leguminosarum can fix 50-60 kg N/ha.',
            'PL-8, DPL-15, IPL-316 are popular high-yielding wilt-resistant varieties.',
            'Spray chlorpyrifos (2 ml/L) for pod borer management if infestation exceeds ETL.',
            'Sulfur (20 kg/ha as gypsum) improves nitrogen fixation and quality.',
            'Lentils can be grown as zero-till crop after paddy harvest with residue management.',
        ],
        'calendar': {
            'Jan': 'Pod fill; protective irrigation',
            'Feb': 'Harvest; threshing',
            'Mar': 'Storage; market; land preparation',
            'Apr': 'Off-season management',
            'May': 'Procure seeds for next season',
            'Jun': 'Deep ploughing; Kharif crop',
            'Jul': 'Kharif management',
            'Aug': 'Kharif management',
            'Sep': 'Pre-sowing irrigation; land preparation',
            'Oct': 'Sowing (Oct 15 - Nov 15)',
            'Nov': 'Weeding; vegetative growth',
            'Dec': 'Flowering; pest monitoring',
        },
    },

    'pomegranate': {
        'fertilizer': {
            'N': 'Urea (625 g/plant/year in 3 splits)',
            'P': 'Single Super Phosphate (375 g/plant/year)',
            'K': 'Muriate of Potash (375 g/plant/year)',
        },
        'irrigation': {
            'frequency': 'Drip irrigation: 25-30 liters/plant/day in summer; 15-20 L in winter',
            'notes': 'Pomegranate is drought-tolerant but responds well to regular drip irrigation.',
        },
        'rotation': ['legumes (intercrop)', 'vegetables (young orchard)'],
        'season': 'Perennial',
        'yield_per_hectare': 18.0,
        'market_price': 8000,
        'timeline': [
            {'stage': 'Planting', 'days': '0-30', 'desc': 'Plant rooted cuttings or air layers in 60x60x60 cm pits at 4.5x3 m spacing.'},
            {'stage': 'Establishment (Yr 1-2)', 'days': '31-730', 'desc': 'Train to single/multi-stem. Formative pruning. Regular irrigation.'},
            {'stage': 'First Crop (Yr 3)', 'days': '731-1095', 'desc': 'Mrig bahar (June-July) flowering. Apply full fertilizer dose.'},
            {'stage': 'Full Bearing', 'days': '1096+', 'desc': 'Annual bahar treatment. 3 bahars possible (Mrig/Hasta/Ambe).'},
            {'stage': 'Fruit Development', 'days': '90-120 days post-flowering', 'desc': 'Bagging with newspaper bags prevents sunburn and borer damage.'},
            {'stage': 'Harvest', 'days': '120-150 days post-flowering', 'desc': 'Harvest when fruits have metallic sound on tapping and reach 200-300g weight.'},
        ],
        'tips': [
            'Practice "bahar treatment" - stress period (water + nutrient) followed by flush irrigation to synchronize flowering.',
            'Mrig bahar (June-July) gives best quality fruit in most regions of India.',
            'Bag fruits with newspaper or non-woven fabric bags after fruit set to prevent borer and sunburn.',
            'Bhendi (okra) can be intercropped in young pomegranate orchards for additional income.',
            'Bacterial blight (Xanthomonas) is the most serious disease - copper-based sprays at intervals.',
        ],
        'calendar': {
            'Jan': 'Harvest Ambe bahar; irrigation',
            'Feb': 'Post-harvest pruning; fertilize',
            'Mar': 'Bahar treatment preparation; stress',
            'Apr': 'Stress period (water withholding)',
            'May': 'Pre-flush fertilizer; resume irrigation',
            'Jun': 'Mrig bahar flush irrigation; flowering',
            'Jul': 'Fruit set; bagging; pest management',
            'Aug': 'Fruit development; irrigation',
            'Sep': 'Fruit maturity; harvest preparation',
            'Oct': 'Harvest Mrig bahar; market',
            'Nov': 'Post-harvest; Hasta bahar preparation',
            'Dec': 'Hasta bahar management; irrigation',
        },
    },

    'mungbean': {
        'fertilizer': {
            'N': 'Urea (20 kg/ha basal - short-duration legume)',
            'P': 'Single Super Phosphate (40 kg/ha)',
            'K': 'Muriate of Potash (20 kg/ha)',
        },
        'irrigation': {
            'frequency': 'Pre-sowing + 2-3 irrigations at branching, flowering, pod fill',
            'notes': 'Short duration (60-65 days) crop. Avoid waterlogging especially at pod fill.',
        },
        'rotation': ['wheat', 'rice', 'maize', 'sorghum'],
        'season': 'Zaid',
        'yield_per_hectare': 0.9,
        'market_price': 7500,
        'timeline': [
            {'stage': 'Sowing', 'days': '0-5', 'desc': 'Seed treatment with Rhizobium + Trichoderma. Sow at 30x10 cm.'},
            {'stage': 'Germination & Establishment', 'days': '6-15', 'desc': 'Ensure moisture. Thin if overcrowded.'},
            {'stage': 'Vegetative Growth', 'days': '16-30', 'desc': 'One weeding. Apply basal fertilizer.'},
            {'stage': 'Flowering', 'days': '31-45', 'desc': 'Irrigation at flowering. Monitor for yellow mosaic virus.'},
            {'stage': 'Pod Fill', 'days': '46-60', 'desc': 'Final irrigation. Monitor for pod borer.'},
            {'stage': 'Harvest', 'days': '61-70', 'desc': 'Multiple pickings as pods mature. Or single harvest after 70-80% pods mature.'},
        ],
        'tips': [
            'Use TARM-18, Pusa Vishal, or PDM-11 varieties for high yield and MYMV resistance.',
            'Mungbean is an excellent green manure crop - plow in to add 40-50 kg N/ha.',
            'Yellow mosaic virus spread by whiteflies - spray imidacloprid at first signs.',
            'Intercrop with maize (2:1) to maximize land use and add nitrogen to soil.',
            'Harvest pods in 2-3 pickings to maximize yield and avoid shattering losses.',
        ],
        'calendar': {
            'Jan': 'Rabi mungbean harvest (south India)',
            'Feb': 'Land preparation; procurement',
            'Mar': 'Zaid sowing begins; irrigate',
            'Apr': 'Vegetative growth; fertilizer; irrigation',
            'May': 'Harvest Zaid mungbean',
            'Jun': 'Kharif sowing begins',
            'Jul': 'Kharif vegetative growth; weed control',
            'Aug': 'Flowering; pod fill; irrigation',
            'Sep': 'Kharif harvest; threshing',
            'Oct': 'Land preparation for Rabi',
            'Nov': 'Rabi sowing (south India)',
            'Dec': 'Vegetative growth; weed management',
        },
    },

    'blackgram': {
        'fertilizer': {
            'N': 'Urea (20 kg/ha basal)',
            'P': 'Single Super Phosphate (40 kg/ha)',
            'K': 'Muriate of Potash (20 kg/ha)',
        },
        'irrigation': {
            'frequency': 'Pre-sowing + 2-3 irrigations at critical stages (branching, flowering, pod fill)',
            'notes': 'Blackgram cannot tolerate waterlogging. Provide good drainage.',
        },
        'rotation': ['rice', 'wheat', 'maize', 'sorghum'],
        'season': 'Kharif',
        'yield_per_hectare': 0.8,
        'market_price': 7000,
        'timeline': [
            {'stage': 'Sowing', 'days': '0-5', 'desc': 'Seed treatment with Rhizobium + fungicide. Sow July (Kharif).'},
            {'stage': 'Germination', 'days': '6-10', 'desc': 'Thinning at 10 days to maintain spacing.'},
            {'stage': 'Vegetative Growth', 'days': '11-30', 'desc': 'Weed control. Apply basal fertilizer.'},
            {'stage': 'Flowering', 'days': '31-45', 'desc': 'Irrigation at flowering. Insecticide if needed.'},
            {'stage': 'Pod Fill', 'days': '46-65', 'desc': 'Maintain moisture. Pod borer monitoring.'},
            {'stage': 'Harvest', 'days': '66-75', 'desc': 'Multiple pickings or single harvest.'},
        ],
        'tips': [
            'Pant U-30, LBG-17, ADT-5 are high-yielding varieties with good disease tolerance.',
            'Yellow mosaic virus is the major disease - use resistant varieties as first management.',
            'Seed inoculation with Bradyrhizobium increases yield by 15-20% without extra N cost.',
            'Timely sowing (July 1-15 for Kharif) is critical for yield optimization.',
            'Spray spinosad for thrips management - thrips cause scarring and quality loss.',
        ],
        'calendar': {
            'Jan': 'Rabi blackgram harvest (south India)',
            'Feb': 'Market; storage; land preparation',
            'Mar': 'Zaid/summer crop if irrigated',
            'Apr': 'Summer crop management',
            'May': 'Summer harvest; kharif prep',
            'Jun': 'Land preparation; pre-sowing irrigation',
            'Jul': 'Kharif sowing (July 1-15)',
            'Aug': 'Vegetative growth; weed management',
            'Sep': 'Flowering; pod fill; irrigation',
            'Oct': 'Kharif harvest; threshing',
            'Nov': 'Rabi sowing (south India)',
            'Dec': 'Rabi vegetative growth; weed control',
        },
    },

    'kidneybeans': {
        'fertilizer': {
            'N': 'Urea (25 kg/ha basal)',
            'P': 'Single Super Phosphate (60 kg/ha)',
            'K': 'Muriate of Potash (30 kg/ha)',
        },
        'irrigation': {
            'frequency': 'Every 7-10 days. Critical at flowering and pod fill stages.',
            'notes': 'Avoid waterlogging. Kidney beans susceptible to root rot in wet conditions.',
        },
        'rotation': ['maize', 'wheat', 'rice', 'sorghum'],
        'season': 'Kharif',
        'yield_per_hectare': 1.5,
        'market_price': 9000,
        'timeline': [
            {'stage': 'Land Preparation', 'days': '0-7', 'desc': 'Well-drained loamy soil preferred. Add FYM 10 t/ha.'},
            {'stage': 'Sowing', 'days': '8-12', 'desc': 'Seed treatment with Rhizobium. Sow at 45x10 cm spacing. Seed rate 80-100 kg/ha.'},
            {'stage': 'Vegetative', 'days': '13-35', 'desc': 'Weeding at 20-25 days. Apply basal fertilizer.'},
            {'stage': 'Flowering', 'days': '36-55', 'desc': 'Irrigation. Spray insecticide for thrips/pod fly.'},
            {'stage': 'Pod Fill', 'days': '56-75', 'desc': 'Irrigation. Monitor for bean pod borer.'},
            {'stage': 'Harvest', 'days': '76-95', 'desc': 'Harvest when pods turn papery. Thresh carefully to avoid seed damage.'},
        ],
        'tips': [
            'Grown primarily in Himalayan states (H.P., J&K, Uttarakhand) - adapted to cool climates.',
            'Pusa Parvati, SFC-118 are popular varieties for high yields in hill conditions.',
            'Anthracnose is the major fungal disease - use Mancozeb (0.25%) spray.',
            'Bush type varieties prefer spacing of 45x10 cm; climbing types need support.',
            'Seed hardness (seed coat impermeability) is a quality parameter - use proper drying.',
        ],
        'calendar': {
            'Jan': 'Rabi harvest in south India',
            'Feb': 'Storage; market',
            'Mar': 'Land preparation for summer/kharif',
            'Apr': 'Summer crop sowing (hills)',
            'May': 'Vegetative growth; irrigation; fertilizer',
            'Jun': 'Kharif sowing begins (plains)',
            'Jul': 'Main Kharif sowing in hills; vegetative stage',
            'Aug': 'Flowering; pod fill; weed management',
            'Sep': 'Harvest hills crop; kharif pod fill (plains)',
            'Oct': 'Kharif harvest plains; threshing',
            'Nov': 'Post-harvest; rabi prep',
            'Dec': 'Off-season management',
        },
    },

    'pigeonpeas': {
        'fertilizer': {
            'N': 'Urea (20 kg/ha basal - N-fixing legume)',
            'P': 'Single Super Phosphate (50 kg/ha)',
            'K': 'Muriate of Potash (20 kg/ha)',
        },
        'irrigation': {
            'frequency': 'Rainfed mostly. 1-2 protective irrigations at pod fill if needed.',
            'notes': 'Deep-rooted and drought-tolerant. Avoid waterlogging. Grown in 600-1500 mm rainfall areas.',
        },
        'rotation': ['sorghum', 'maize', 'rice', 'cotton'],
        'season': 'Kharif',
        'yield_per_hectare': 1.5,
        'market_price': 7200,
        'timeline': [
            {'stage': 'Land Preparation', 'days': '0-7', 'desc': 'Deep ploughing. Seed inoculation with Rhizobium.'},
            {'stage': 'Sowing', 'days': '8-12', 'desc': 'Sow June-July at 75x30 cm spacing. Seed rate 15-20 kg/ha.'},
            {'stage': 'Vegetative Growth', 'days': '13-60', 'desc': 'Two weedings at 20 and 40 days. Avoid N top-dressing.'},
            {'stage': 'Flowering', 'days': '61-120', 'desc': 'Long flowering period (30-60 days). Monitor for pod borer.'},
            {'stage': 'Pod Fill', 'days': '121-160', 'desc': 'Pod borer management critical. Protective irrigation if dry.'},
            {'stage': 'Harvest', 'days': '161-180', 'desc': 'Short-duration varieties: 120-130 days; Long-duration: 180-270 days.'},
        ],
        'tips': [
            'Intercrop with sorghum (1:2 or 1:3) for risk management in rainfed conditions.',
            'ICPH-2671 (hybrid) gives 2-3 t/ha yield - significantly higher than local varieties.',
            'Use sex pheromone traps and NPV (250 LE/ha) for pod borer management.',
            'Wilt-resistant varieties (Pusa Ageti, Maruti) important in wilt-endemic areas.',
            'Promote pigeonpeas in low-fertility and drought-prone areas - very hardy crop.',
        ],
        'calendar': {
            'Jan': 'Late harvest (long-duration varieties)',
            'Feb': 'Threshing; storage; market',
            'Mar': 'Land preparation; off-season management',
            'Apr': 'Deep ploughing; procure seeds',
            'May': 'Procure inputs; soil testing',
            'Jun': 'Sowing (June 15 - July 15)',
            'Jul': 'Sowing completion; thinning; weeding',
            'Aug': 'Weeding; weed management',
            'Sep': 'Flowering begins; pod borer monitoring',
            'Oct': 'Pod fill; pest management',
            'Nov': 'Short-duration varieties harvest',
            'Dec': 'Long-duration varieties pod fill',
        },
    },

    'mothbeans': {
        'fertilizer': {
            'N': 'Urea (15 kg/ha basal)',
            'P': 'Single Super Phosphate (25 kg/ha)',
            'K': 'Muriate of Potash (15 kg/ha)',
        },
        'irrigation': {
            'frequency': 'Largely rainfed. 1-2 irrigations for summer crop.',
            'notes': 'Mothbean is the most drought-tolerant pulse in India. Minimal water requirement.',
        },
        'rotation': ['bajra (pearl millet)', 'sorghum', 'maize'],
        'season': 'Kharif',
        'yield_per_hectare': 0.7,
        'market_price': 6000,
        'timeline': [
            {'stage': 'Sowing', 'days': '0-5', 'desc': 'Sow June-July. Seed rate 12-15 kg/ha. Broad cast or line sow.'},
            {'stage': 'Germination', 'days': '6-10', 'desc': 'Ensure adequate moisture during germination.'},
            {'stage': 'Vegetative Growth', 'days': '11-30', 'desc': 'Minimal weeding. Drought-tolerant - minimal inputs needed.'},
            {'stage': 'Flowering', 'days': '31-50', 'desc': 'Crop sets flowers under rain stress too. Very resilient.'},
            {'stage': 'Pod Fill', 'days': '51-65', 'desc': 'Continue monitoring. Pods mature indeterminately.'},
            {'stage': 'Harvest', 'days': '66-80', 'desc': 'Multiple pickings recommended. Or single harvest when 80% pods mature.'},
        ],
        'tips': [
            'Ideal for arid and semi-arid regions (Rajasthan, Gujarat) in sandy loam soils.',
            'Variety RMO-257 and CAZRI Moth-2 are popular high-yielding varieties.',
            'Mothbeans fix nitrogen and improve soil fertility for subsequent crops.',
            'Can be grown on eroded lands and in nutrient-deficient soils - excellent rehabilitation crop.',
            'Store in sealed bins with 9% moisture content to avoid weevil damage.',
        ],
        'calendar': {
            'Jan': 'Off-season; storage management',
            'Feb': 'Land preparation for summer crop',
            'Mar': 'Summer sowing if irrigated',
            'Apr': 'Summer crop management',
            'May': 'Summer harvest; kharif preparation',
            'Jun': 'Kharif sowing (June 15 - July 15)',
            'Jul': 'Vegetative growth; minimal inputs needed',
            'Aug': 'Flowering; pod development',
            'Sep': 'Harvest (multiple pickings)',
            'Oct': 'Threshing; storage; market',
            'Nov': 'Post-harvest; land preparation',
            'Dec': 'Off-season',
        },
    },
}


# ---------------------------------------------------------------------------
# MARKET PRICES
# ---------------------------------------------------------------------------

MARKET_PRICES = [
    {'crop': 'Rice',        'price': 2183,  'unit': 'quintal', 'trend': 'stable', 'category': 'Cereal'},
    {'crop': 'Wheat',       'price': 2275,  'unit': 'quintal', 'trend': 'up',     'category': 'Cereal'},
    {'crop': 'Maize',       'price': 1870,  'unit': 'quintal', 'trend': 'up',     'category': 'Cereal'},
    {'crop': 'Chickpea',    'price': 5400,  'unit': 'quintal', 'trend': 'stable', 'category': 'Pulse'},
    {'crop': 'Lentil',      'price': 5500,  'unit': 'quintal', 'trend': 'up',     'category': 'Pulse'},
    {'crop': 'Mungbean',    'price': 7500,  'unit': 'quintal', 'trend': 'up',     'category': 'Pulse'},
    {'crop': 'Blackgram',   'price': 7000,  'unit': 'quintal', 'trend': 'stable', 'category': 'Pulse'},
    {'crop': 'Pigeonpeas',  'price': 7200,  'unit': 'quintal', 'trend': 'down',   'category': 'Pulse'},
    {'crop': 'Kidneybeans', 'price': 9000,  'unit': 'quintal', 'trend': 'stable', 'category': 'Pulse'},
    {'crop': 'Mothbeans',   'price': 6000,  'unit': 'quintal', 'trend': 'stable', 'category': 'Pulse'},
    {'crop': 'Cotton',      'price': 6620,  'unit': 'quintal', 'trend': 'up',     'category': 'Cash Crop'},
    {'crop': 'Jute',        'price': 4300,  'unit': 'quintal', 'trend': 'stable', 'category': 'Cash Crop'},
    {'crop': 'Coffee',      'price': 18000, 'unit': 'quintal', 'trend': 'up',     'category': 'Cash Crop'},
    {'crop': 'Groundnut',   'price': 5800,  'unit': 'quintal', 'trend': 'up',     'category': 'Cash Crop'},
    {'crop': 'Banana',      'price': 1500,  'unit': 'quintal', 'trend': 'stable', 'category': 'Fruit'},
    {'crop': 'Mango',       'price': 4000,  'unit': 'quintal', 'trend': 'up',     'category': 'Fruit'},
    {'crop': 'Grapes',      'price': 5000,  'unit': 'quintal', 'trend': 'stable', 'category': 'Fruit'},
    {'crop': 'Watermelon',  'price': 600,   'unit': 'quintal', 'trend': 'stable', 'category': 'Fruit'},
    {'crop': 'Coconut',     'price': 2800,  'unit': 'quintal', 'trend': 'up',     'category': 'Fruit'},
    {'crop': 'Papaya',      'price': 1200,  'unit': 'quintal', 'trend': 'down',   'category': 'Fruit'},
    {'crop': 'Orange',      'price': 3500,  'unit': 'quintal', 'trend': 'up',     'category': 'Fruit'},
    {'crop': 'Apple',       'price': 7000,  'unit': 'quintal', 'trend': 'stable', 'category': 'Fruit'},
    {'crop': 'Pomegranate', 'price': 8000,  'unit': 'quintal', 'trend': 'up',     'category': 'Fruit'},
]


# ---------------------------------------------------------------------------
# SEASONAL CROP LISTS
# ---------------------------------------------------------------------------

KHARIF_CROPS = ['rice', 'maize', 'cotton', 'groundnut', 'jute', 'pigeonpeas', 'mothbeans', 'mungbean', 'blackgram', 'papaya']
RABI_CROPS   = ['wheat', 'chickpea', 'lentil', 'apple', 'orange']
ZAID_CROPS   = ['watermelon', 'mungbean']
PERENNIAL_CROPS = ['banana', 'mango', 'grapes', 'coconut', 'coffee', 'pomegranate']


# ---------------------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------------------

def calculate_soil_health(N, P, K, ph):
    """
    Calculate a soil health score (0-100) based on N, P, K levels and pH.
    Returns a dict with score, status, alerts, and individual nutrient statuses.
    """
    score = 0
    alerts = []

    # --- Nitrogen (N) ---
    if N < 20:
        n_status = 'Low'
        n_score = 5
        alerts.append({'type': 'danger', 'message': f'Nitrogen is critically low ({N} kg/ha). Apply nitrogenous fertilizer immediately.'})
    elif 20 <= N <= 40:
        n_status = 'Low'
        n_score = 12
        alerts.append({'type': 'warning', 'message': f'Nitrogen is below optimal ({N} kg/ha). Consider nitrogen supplementation.'})
    elif 40 < N <= 80:
        n_status = 'Optimal'
        n_score = 25
    elif 80 < N <= 140:
        n_status = 'Optimal'
        n_score = 22
    elif 140 < N <= 200:
        n_status = 'High'
        n_score = 18
        alerts.append({'type': 'info', 'message': f'Nitrogen is slightly high ({N} kg/ha). Reduce N fertilizer dosage.'})
    else:
        n_status = 'Excessive'
        n_score = 10
        alerts.append({'type': 'danger', 'message': f'Nitrogen is excessive ({N} kg/ha). Risk of nitrate leaching and crop burn.'})

    # --- Phosphorus (P) ---
    if P < 10:
        p_status = 'Low'
        p_score = 5
        alerts.append({'type': 'danger', 'message': f'Phosphorus is critically low ({P} kg/ha). Apply SSP or DAP immediately.'})
    elif 10 <= P <= 25:
        p_status = 'Low'
        p_score = 12
        alerts.append({'type': 'warning', 'message': f'Phosphorus is below optimal ({P} kg/ha). Supplement with phosphatic fertilizer.'})
    elif 25 < P <= 50:
        p_status = 'Optimal'
        p_score = 25
    elif 50 < P <= 80:
        p_status = 'Optimal'
        p_score = 22
    elif 80 < P <= 120:
        p_status = 'High'
        p_score = 17
        alerts.append({'type': 'info', 'message': f'Phosphorus is high ({P} kg/ha). Phosphorus fixation may limit availability.'})
    else:
        p_status = 'Excessive'
        p_score = 8
        alerts.append({'type': 'danger', 'message': f'Phosphorus is excessive ({P} kg/ha). May cause micronutrient deficiencies (Zn, Fe).'})

    # --- Potassium (K) ---
    if K < 10:
        k_status = 'Low'
        k_score = 5
        alerts.append({'type': 'danger', 'message': f'Potassium is critically low ({K} kg/ha). Apply MOP or SOP urgently.'})
    elif 10 <= K <= 25:
        k_status = 'Low'
        k_score = 12
        alerts.append({'type': 'warning', 'message': f'Potassium is below optimal ({K} kg/ha). Apply potassic fertilizer.'})
    elif 25 < K <= 50:
        k_status = 'Optimal'
        k_score = 25
    elif 50 < K <= 80:
        k_status = 'Optimal'
        k_score = 22
    elif 80 < K <= 120:
        k_status = 'High'
        k_score = 17
        alerts.append({'type': 'info', 'message': f'Potassium is high ({K} kg/ha). Excess K may reduce Mg uptake.'})
    else:
        k_status = 'Excessive'
        k_score = 8
        alerts.append({'type': 'danger', 'message': f'Potassium is excessive ({K} kg/ha). Reduce potassic fertilizer application.'})

    # --- pH ---
    if ph < 4.5:
        ph_status = 'Very Acidic'
        ph_score = 3
        alerts.append({'type': 'danger', 'message': f'Soil pH is extremely acidic ({ph}). Apply lime (2-5 t/ha) urgently. Most nutrients unavailable.'})
    elif 4.5 <= ph < 5.5:
        ph_status = 'Acidic'
        ph_score = 8
        alerts.append({'type': 'warning', 'message': f'Soil pH is acidic ({ph}). Apply agricultural lime (1-2 t/ha) to raise pH.'})
    elif 5.5 <= ph < 6.0:
        ph_status = 'Slightly Acidic'
        ph_score = 15
        alerts.append({'type': 'info', 'message': f'Soil pH is slightly acidic ({ph}). Suitable for acid-tolerant crops. Some micronutrients may be limited.'})
    elif 6.0 <= ph <= 7.0:
        ph_status = 'Optimal'
        ph_score = 25
    elif 7.0 < ph <= 7.5:
        ph_status = 'Slightly Alkaline'
        ph_score = 20
        alerts.append({'type': 'info', 'message': f'Soil pH is slightly alkaline ({ph}). Apply gypsum or sulfur to reduce pH gradually.'})
    elif 7.5 < ph <= 8.0:
        ph_status = 'Alkaline'
        ph_score = 12
        alerts.append({'type': 'warning', 'message': f'Soil pH is alkaline ({ph}). Micronutrient deficiencies likely. Apply gypsum and organic matter.'})
    elif 8.0 < ph <= 9.0:
        ph_status = 'Highly Alkaline'
        ph_score = 6
        alerts.append({'type': 'danger', 'message': f'Soil pH is highly alkaline ({ph}). Sodic soil likely. Reclamation needed with gypsum + green manure.'})
    else:
        ph_status = 'Extremely Alkaline'
        ph_score = 2
        alerts.append({'type': 'danger', 'message': f'Soil pH is extreme ({ph}). Soil unsuitable for most crops without major reclamation.'})

    score = n_score + p_score + k_score + ph_score

    if score >= 85:
        status = 'Excellent'
    elif score >= 65:
        status = 'Good'
    elif score >= 45:
        status = 'Moderate'
    else:
        status = 'Poor'

    return {
        'score': score,
        'status': status,
        'alerts': alerts,
        'n_status': n_status,
        'p_status': p_status,
        'k_status': k_status,
        'ph_status': ph_status,
    }


def get_current_season():
    """
    Returns the current agricultural season and recommended crops based on month.
    """
    month = datetime.datetime.now().month

    if month in [6, 7, 8, 9]:
        season_name = 'Kharif'
        recommended_crops = KHARIF_CROPS
    elif month in [10, 11, 12, 1, 2, 3]:
        season_name = 'Rabi'
        recommended_crops = RABI_CROPS
    else:  # March, April, May
        season_name = 'Zaid'
        recommended_crops = ZAID_CROPS

    return {
        'name': season_name,
        'recommended_crops': recommended_crops,
    }


def get_fertilizer_recommendation(crop, N, P, K):
    """
    Returns a list of fertilizer recommendations based on crop requirements and
    current soil nutrient levels.
    """
    crop_lower = crop.lower()
    crop_info = CROP_DATA.get(crop_lower, {})
    fertilizer_info = crop_info.get('fertilizer', {})

    recommendations = []

    n_fert = fertilizer_info.get('N', 'Urea (120 kg/ha)')
    p_fert = fertilizer_info.get('P', 'Single Super Phosphate (60 kg/ha)')
    k_fert = fertilizer_info.get('K', 'Muriate of Potash (40 kg/ha)')

    # Nitrogen
    if N < 40:
        reason = f'Soil N is LOW ({N} kg/ha). Urgent supplementation needed.'
        amount = 'Full dose as recommended'
    elif 40 <= N <= 80:
        reason = f'Soil N is moderate ({N} kg/ha). Standard dose advised.'
        amount = 'Standard dose'
    else:
        reason = f'Soil N is HIGH ({N} kg/ha). Reduce dosage by 30-40%.'
        amount = 'Reduced dose (60-70% of recommendation)'

    recommendations.append({
        'nutrient': 'Nitrogen (N)',
        'fertilizer_name': n_fert,
        'amount': amount,
        'reason': reason,
    })

    # Phosphorus
    if P < 25:
        reason = f'Soil P is LOW ({P} kg/ha). Apply full phosphatic fertilizer.'
        amount = 'Full dose as recommended'
    elif 25 <= P <= 50:
        reason = f'Soil P is moderate ({P} kg/ha). Standard dose advised.'
        amount = 'Standard dose'
    else:
        reason = f'Soil P is HIGH ({P} kg/ha). Skip or halve P application.'
        amount = 'Skip or apply half dose'

    recommendations.append({
        'nutrient': 'Phosphorus (P)',
        'fertilizer_name': p_fert,
        'amount': amount,
        'reason': reason,
    })

    # Potassium
    if K < 25:
        reason = f'Soil K is LOW ({K} kg/ha). Apply full potassic fertilizer.'
        amount = 'Full dose as recommended'
    elif 25 <= K <= 50:
        reason = f'Soil K is moderate ({K} kg/ha). Standard dose advised.'
        amount = 'Standard dose'
    else:
        reason = f'Soil K is HIGH ({K} kg/ha). Reduce K application significantly.'
        amount = 'Reduced dose or skip this season'

    recommendations.append({
        'nutrient': 'Potassium (K)',
        'fertilizer_name': k_fert,
        'amount': amount,
        'reason': reason,
    })

    return recommendations


def estimate_yield_profit(crop, land_size_acres):
    """
    Estimates yield and profit based on crop and land size.
    Returns dict with estimated_yield, estimated_revenue, estimated_cost, estimated_profit.
    """
    crop_lower = crop.lower()
    crop_info = CROP_DATA.get(crop_lower, {})

    yield_per_ha = crop_info.get('yield_per_hectare', 2.0)
    market_price_per_quintal = crop_info.get('market_price', 2000)

    # Convert acres to hectares (1 acre = 0.4047 ha)
    land_size_ha = land_size_acres * 0.4047

    # Estimated yield in tons
    estimated_yield_tons = yield_per_ha * land_size_ha

    # Convert tons to quintals (1 ton = 10 quintals)
    estimated_yield_quintals = estimated_yield_tons * 10

    # Revenue
    estimated_revenue = int(estimated_yield_quintals * market_price_per_quintal)

    # Cost estimation per acre
    cost_per_acre_map = {
        'rice':        22000,
        'wheat':       18000,
        'maize':       17000,
        'cotton':      25000,
        'chickpea':    12000,
        'lentil':      12000,
        'mungbean':    10000,
        'blackgram':   10000,
        'pigeonpeas':  11000,
        'mothbeans':   8000,
        'kidneybeans': 14000,
        'jute':        15000,
        'groundnut':   20000,
        'watermelon':  20000,
        'banana':      30000,
        'mango':       25000,
        'grapes':      50000,
        'coconut':     15000,
        'coffee':      35000,
        'papaya':      22000,
        'orange':      28000,
        'apple':       40000,
        'pomegranate': 32000,
    }

    cost_per_acre = cost_per_acre_map.get(crop_lower, 18000)
    estimated_cost = int(cost_per_acre * land_size_acres)
    estimated_profit = estimated_revenue - estimated_cost

    return {
        'estimated_yield': round(estimated_yield_tons, 2),
        'estimated_revenue': estimated_revenue,
        'estimated_cost': estimated_cost,
        'estimated_profit': estimated_profit,
    }

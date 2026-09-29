"""
Curated Realistic CPSE Material Catalog Datasets.
Emulates legacy material records from IOCL (Oil & Gas), NTPC (Power), SAIL (Steel), and BHEL (Heavy Engg).
Includes known duplicates, abbreviation variations, and functionally equivalent items.
"""

from typing import List
from src.models.material import RawMaterialRecord, CPSEIdentifier

SAMPLE_CPSE_DATASETS: List[RawMaterialRecord] = [
    # --- CLUSTER A: 2" Ball Valve Class 150 Flanged SS316 (Known 3-way duplicate across Oil, Power, Steel) ---
    RawMaterialRecord(
        cpse_id=CPSEIdentifier.IOCL,
        local_material_code="IOC-MTR-402911",
        raw_description="VALVE, BALL, 2 INCH, 150#, FLGD RF, BODY SS316, TRIM SS316, ASME B16.34",
        raw_uom="NOS",
        category_hint="Piping & Valves",
        plant_location="Mathura Refinery",
        unit_price_inr=14500.0,
        stock_quantity=45
    ),
    RawMaterialRecord(
        cpse_id=CPSEIdentifier.NTPC,
        local_material_code="NTPC-MECH-88210",
        raw_description="BALL VALVE 50 NB CL-150 FLANGED RAISED FACE S.S. 316 BODY/TRIM TO B16.34",
        raw_uom="PCS",
        category_hint="Mechanical Valves",
        plant_location="Ramagundam STPS",
        unit_price_inr=15200.0,
        stock_quantity=22
    ),
    RawMaterialRecord(
        cpse_id=CPSEIdentifier.SAIL,
        local_material_code="SAIL-BSP-VAL-00431",
        raw_description="VLV BALL 2\" 150 LBS RF FLG BODY STAINLESS STEEL 316 ASME-B16.34 LEVER OPERATED",
        raw_uom="EA",
        category_hint="Valves & Spares",
        plant_location="Bhilai Steel Plant",
        unit_price_inr=14850.0,
        stock_quantity=18
    ),

    # --- CLUSTER B: M16x65 Hex Bolt Grade 8.8 Galvanized with Nut (Known 3-way duplicate) ---
    RawMaterialRecord(
        cpse_id=CPSEIdentifier.IOCL,
        local_material_code="IOC-FAST-10928",
        raw_description="BOLT, HEX, M16 X 65 MM, HT GR 8.8, GALV, WITH NUT, IS:1363 / ISO 4014",
        raw_uom="NOS",
        category_hint="Fasteners",
        plant_location="Panipat Refinery",
        unit_price_inr=75.0,
        stock_quantity=1200
    ),
    RawMaterialRecord(
        cpse_id=CPSEIdentifier.NTPC,
        local_material_code="NTPC-FST-44910",
        raw_description="FASTENER HEX BOLT M16X65 CLASS 8.8 GALVANIZED C/W HEX NUT IS 1363",
        raw_uom="PC",
        category_hint="Hardware & Fasteners",
        plant_location="Singrauli TPP",
        unit_price_inr=82.0,
        stock_quantity=2500
    ),
    RawMaterialRecord(
        cpse_id=CPSEIdentifier.BHEL,
        local_material_code="BHEL-HYD-BOLT-992",
        raw_description="HEX HEAD BOLT DIA M16 LENGTH 65MM GRADE 8.8 GI WITH ONE NUT REF IS 1363",
        raw_uom="NOS",
        category_hint="Turbine Fasteners",
        plant_location="BHEL Hyderabad",
        unit_price_inr=78.0,
        stock_quantity=800
    ),

    # --- CLUSTER C: Seamless Carbon Steel Pipe 4" Sch 40 ASTM A106 Gr.B (Known 2-way duplicate) ---
    RawMaterialRecord(
        cpse_id=CPSEIdentifier.IOCL,
        local_material_code="IOC-PIP-77312",
        raw_description="PIPE, CS, SMLS, 4\" NB, SCH 40, ASTM A106 GR.B, BE, ASME B36.10",
        raw_uom="MTR",
        category_hint="Pipes & Tubes",
        plant_location="Gujarat Refinery",
        unit_price_inr=2100.0,
        stock_quantity=350
    ),
    RawMaterialRecord(
        cpse_id=CPSEIdentifier.SAIL,
        local_material_code="SAIL-RSP-PIPE-102",
        raw_description="CARBON STEEL SEAMLESS PIPES 100MM NB SCHEDULE 40 MATERIAL ASTM A-106 GRADE B BEVEL END",
        raw_uom="METRE",
        category_hint="Piping Materials",
        plant_location="Rourkela Steel Plant",
        unit_price_inr=2050.0,
        stock_quantity=500
    ),

    # --- CLUSTER D: Deep Groove Ball Bearing 6205-2RS (Known 3-way duplicate) ---
    RawMaterialRecord(
        cpse_id=CPSEIdentifier.NTPC,
        local_material_code="NTPC-BRG-3019",
        raw_description="BEARING DEEP GROOVE BALL 6205 2RS C3 SKF/FAG RUBBER SEAL",
        raw_uom="NOS",
        category_hint="Bearings",
        plant_location="Talcher STPS",
        unit_price_inr=320.0,
        stock_quantity=95
    ),
    RawMaterialRecord(
        cpse_id=CPSEIdentifier.BHEL,
        local_material_code="BHEL-TRICHY-BRG-55",
        raw_description="BALL BEARING, DGBB, NO: 6205-2RS, DOUBLE CONTACT SEAL, CLEARANCE C3",
        raw_uom="PCS",
        category_hint="Motors & Spares",
        plant_location="BHEL Trichy",
        unit_price_inr=310.0,
        stock_quantity=110
    ),
    RawMaterialRecord(
        cpse_id=CPSEIdentifier.SAIL,
        local_material_code="SAIL-BSL-BRG-8802",
        raw_description="RADIAL BALL BEARING 6205-2RS/C3 MAKE SKF/FAG/NBC",
        raw_uom="EA",
        category_hint="Mechanical Spares",
        plant_location="Bokaro Steel Plant",
        unit_price_inr=335.0,
        stock_quantity=70
    ),

    # --- CLUSTER E: Spiral Wound Gasket 3" Class 300 SS316 with Graphite Filler (Known 2-way duplicate) ---
    RawMaterialRecord(
        cpse_id=CPSEIdentifier.IOCL,
        local_material_code="IOC-GSK-5521",
        raw_description="GASKET, SPIRAL WOUND, 3 INCH, 300#, INNER RING SS316, HOOP SS316, FILLER GRAPHITE, ASME B16.20",
        raw_uom="NOS",
        category_hint="Seals & Gaskets",
        plant_location="Paradip Refinery",
        unit_price_inr=480.0,
        stock_quantity=220
    ),
    RawMaterialRecord(
        cpse_id=CPSEIdentifier.NTPC,
        local_material_code="NTPC-GSK-9011",
        raw_description="SP. WOUND GASKET 80 NB CLASS 300 RF SS316/FLEXIBLE GRAPHITE ASME B16.20 WITH CS OUTER RING",
        raw_uom="NOS",
        category_hint="Boiler Gaskets",
        plant_location="Kudgi STPP",
        unit_price_inr=510.0,
        stock_quantity=180
    ),

    # --- DISTINCT NON-DUPLICATES (Control items to test specificity / avoid false positives) ---
    RawMaterialRecord(
        cpse_id=CPSEIdentifier.IOCL,
        local_material_code="IOC-VLV-9901",
        raw_description="VALVE, GATE, 6 INCH, 600#, FLANGED RF, BODY WCB, TRIM 13CR, API 600",
        raw_uom="NOS",
        category_hint="Piping & Valves",
        plant_location="Panipat Refinery",
        unit_price_inr=48000.0,
        stock_quantity=10
    ),
    RawMaterialRecord(
        cpse_id=CPSEIdentifier.NTPC,
        local_material_code="NTPC-ELEC-4102",
        raw_description="XLPE ARMOURED CABLE 3.5 CORE 240 SQ.MM 1.1KV COPPER CONDUCTOR IS 7098",
        raw_uom="MTR",
        category_hint="Electrical Cables",
        plant_location="Vindhyachal STPS",
        unit_price_inr=1850.0,
        stock_quantity=800
    ),
    RawMaterialRecord(
        cpse_id=CPSEIdentifier.SAIL,
        local_material_code="SAIL-CIV-0091",
        raw_description="PORTLAND POZZOLANA CEMENT (PPC) 50 KG BAG CONFIRMING TO IS 1489",
        raw_uom="BAG",
        category_hint="Civil Materials",
        plant_location="Durgapur Steel Plant",
        unit_price_inr=360.0,
        stock_quantity=2000
    )
]

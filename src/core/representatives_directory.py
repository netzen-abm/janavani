from typing import Dict, Any, Optional

# Static operational data mapping for legislative routing.
# Covers South Indian and North East Indian constituencies explicitly.
LEGISLATIVE_DIRECTORY: Dict[str, Dict[str, Any]] = {
    # --- SOUTH INDIA REGIONAL BOUNDARIES ---
    "CONSTITUENCY-KL-TVM": {
        "state": "Kerala",
        "region": "South India",
        "district": "Thiruvananthapuram",
        "mp_name": "Shri. Shashi Tharoor",
        "mp_email": "shashi.tharoor@sansad.nic.in",
        "mla_name": "Shri. Antony Raju",
        "mla_email": "antony.raju@niyamasabha.nic.in",
        "lsgd_body": "Thiruvananthapuram Municipal Corporation Desk",
        "lsgd_email": "secretarytvm@gmail.com"
    },
    "CONSTITUENCY-KA-BLR-C": {
        "state": "Karnataka",
        "region": "South India",
        "district": "Bengaluru Urban",
        "mp_name": "Shri. P. C. Mohan",
        "mp_email": "pc.mohan@sansad.nic.in",
        "mla_name": "Shri. N. A. Haris",
        "mla_email": "na.haris@karnatakaassembly.gov.in",
        "lsgd_body": "Bruhat Bengaluru Mahanagara Palike Central Division",
        "lsgd_email": "comm@bbmp.gov.in"
    },
    # --- NORTH EAST INDIA REGIONAL BOUNDARIES ---
    "CONSTITUENCY-AS-GHY": {
        "state": "Assam",
        "region": "North East India",
        "district": "Kamrup Metropolitan",
        "mp_name": "Smt. Bijuli Kalita Medhi",
        "mp_email": "bijuli.kalita@sansad.nic.in",
        "mla_name": "Shri. Siddhartha Bhattacharya",
        "mla_email": "siddhartha.bhat@assam.gov.in",
        "lsgd_body": "Guwahati Municipal Corporation Head Office",
        "lsgd_email": "gmc@assam.gov.in"
    },
    "CONSTITUENCY-ML-SHL": {
        "state": "Meghalaya",
        "region": "North East India",
        "district": "East Khasi Hills",
        "mp_name": "Shri. Ricky Andrew J. Syngkon",
        "mp_email": "ricky.syngkon@sansad.nic.in",
        "mla_name": "Shri. Ampareen Lyngdoh",
        "mla_email": "ampareen.lyngdoh@meghalayaassembly.gov.in",
        "lsgd_body": "Shillong Municipal Board Administrative Desk",
        "lsgd_email": "smb-meg@nic.in"
    }
}

def lookup_representatives(constituency_code: str) -> Optional[Dict[str, Any]]:
    """Fetches legislative communication details based on targeted geographic codes."""
    return LEGISLATIVE_DIRECTORY.get(constituency_code)

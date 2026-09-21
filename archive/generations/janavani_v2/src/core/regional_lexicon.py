from typing import Dict, Any

REGIONAL_LEGAL_LEXICON: Dict[str, Dict[str, str]] = {
    "English": {
        "preamble_anchor": "WE, THE PEOPLE OF INDIA, having solemnly resolved to constitute India into a SOVEREIGN SOCIALIST SECULAR DEMOCRATIC REPUBLIC...",
        "it_act_notice": "Please acknowledge receipt of this email (electronic record) u/s 12(1) of the Information Technology Act, 2000.",
        "subject_prefix": "SUBJECT:",
        "prayer_prefix": "PRAYER / DISCIPLINARY DEMAND MATRIX:"
    },
    "Malayalam": {
        "preamble_anchor": "ഭാരതത്തിലെ ജനങ്ങളായ നാം, ഇൻഡ്യയെ ഒരു പരമാധികാര സോഷ്യലിസ്റ്റ് മതേതര ജനാധിപത്യ റിപ്പബ്ലിക്കായി രൂപീകരിക്കുന്നതിന്...",
        "it_act_notice": "2000-ലെ ഇൻഫർമേഷൻ ടെക്നോളജി ആക്ട് സെക്ഷൻ 12(1) പ്രകാരം ഈ ഇമെയിലിന്റെ (ഇലക്ട്രോണിക് റെക്കോർഡ്) രസീത് ദയവായി സാക്ഷ്യപ്പെടുത്തുക.",
        "subject_prefix": "വിഷയം:",
        "prayer_prefix": "ആവശ്യപ്പെടുന്ന പരിഹാരങ്ങൾ / അച്ചടക്ക നടപടികൾ:"
    },
    "Kannada": {
        "preamble_anchor": "ಭಾರತದ ജനಗಳಾದ ನಾವು, ಭಾರತವನ್ನು ಒಂದು ಸಾರ್ವಭೌಮ, ಸಮಾಜವಾದಿ, ಧರ್ಮನಿರಪೇಕ್ಷ, ಪ್ರಜಾಸತ್ತಾತ್ಮಕ ಗಣರಾಜ್ಯವಾಗಿ...",
        "it_act_notice": "ಮಾಹಿತಿ ತಂತ್ರಜ್ಞಾನ ಕಾಯ್ದೆ 2000 ರ ಸೆಕ್ಷನ್ 12(1) ರ ಅಡಿಯಲ್ಲಿ ಈ ಇಮೇಲ್ (ಎಲೆಕ್ಟ್ರಾನಿಕ್ ದಾಖಲೆ) ಸ್ವೀಕೃತಿಯನ್ನು ದಯವಿಟ್ಟು ಖಚಿತಪಡಿಸಿ.",
        "subject_prefix": "ವಿಷಯ:",
        "prayer_prefix": "ಮನವಿ ಮತ್ತು ಶಿಸ್ತು ಕ್ರಮಗಳ ಬೇಡಿಕೆ:"
    },
    "Tamil": {
        "preamble_anchor": "இந்திய மக்களாகிய நாம், இந்தியாவை ஒரு இறையாண்மைமிக்க, சமதர்ம, மதச்சார்பற்ற, மக்களாட்சி குடியரசாக...",
        "it_act_notice": "தகவல் தொழில்நுட்பச் சட்டம், 2000-ன் பிரிவு 12(1)-ன் கீழ் இந்த மின்னஞ்சலின் (மின்னணு ದಾಖலை) ಸ್ವೀகரிப்பை உறுதிப்படுத்தவும்.",
        "subject_prefix": "பொருள்:",
        "prayer_prefix": "கோரிக்கை ಮತ್ತು ஒழுங்குமுறை நடவடிக்கை கோரிக்கைகள்:"
    },
    "Hindi": {
        "preamble_anchor": "हम, भारत के लोग, भारत को एक सम्पूर्ण प्रभुत्व-सम्पन्न समाजवादी पंथनिरपेक्ष लोकतंत्रात्मक गणराज्य बनाने के लिए...",
        "it_act_notice": "कृपया सूचना प्रौद्योगिकी अधिनियम, 2000 की धारा 12(1) के तहत इस ईमेल (इलेक्ट्रॉनिक रिकॉर्ड) की पावती स्वीकार करें।",
        "subject_prefix": "विषय:",
        "prayer_prefix": "प्रार्थना / अनुशासनात्मक मांग विवरण:"
    },
    "Assamese": {
        "preamble_anchor": "আমি, ভাৰতবৰ্ষৰ জনগণে, ভাৰতবৰ্ষক এখন সাৰ্বভৌম সমাজতন্ত্ৰী ধৰ্মনিৰপেক্ষ গণতান্ত্ৰিক গণৰাজ্য ৰূপে গঢ়ি তুলিবলৈ...",
        "it_act_notice": "অনুগ্ৰহ কৰি তথ্য প্ৰযুক্তি আইন, ২০০০ ৰ ধাৰা ১২(১) ৰ অধীনত এই ইমেইলৰ (ইলেক্ট্ৰনিক ৰেকৰ্ড) প্ৰাপ্তি স্বীকাৰ কৰক।",
        "subject_prefix": "বিষয়:",
        "prayer_prefix": "প্ৰাৰ্থনা / অনুশাসনমূলক দাবী সংক্ৰান্তীয় থুল:"
    }
}

def fetch_lexicon_by_language(language_name: str) -> Dict[str, str]:
    """Retrieves target operational translation string blocks securely from local memory structures."""
    return REGIONAL_LEGAL_LEXICON.get(language_name, REGIONAL_LEGAL_LEXICON["English"])

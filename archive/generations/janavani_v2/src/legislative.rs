use serde::{Serialize, Deserialize};

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct ConstitutionalAuditReport {
    pub bill_title: String,
    pub target_legislative_body: String,
    pub golden_triangle_compliance: bool,
    pub article_14_breach: Option<String>,
    pub article_19_breach: Option<String>,
    pub article_21_breach: Option<String>,
    pub directive_principles_alignment: String,
}

pub struct LegislativeMonitor;

impl LegislativeMonitor {
    pub fn audit_bill(title: &str, summary: &str) -> ConstitutionalAuditReport {
        let contains_surveillance = summary.contains("tracking") || summary.contains("identity");
        let contains_restriction = summary.contains("licensing") || summary.contains("assembly");

        ConstitutionalAuditReport {
            bill_title: title.to_string(),
            target_legislative_body: "Parliament of India / State Legislative Assembly".to_string(),
            golden_triangle_compliance: !contains_surveillance && !contains_restriction,
            article_14_breach: if contains_surveillance { Some("Arbitrary digital discrimination classification detected.".to_string()) } else { None },
            article_19_breach: if contains_restriction { Some("Unreasonable restrictions placed on peaceful expression/assembly.".to_string()) } else { None },
            article_21_breach: if contains_surveillance { Some("Infringes upon informational privacy rights under the Puttaswamy framework.".to_string()) } else { None },
            directive_principles_alignment: "Evaluated against Article 47 public health and security metrics.".to_string(),
        }
    }
}

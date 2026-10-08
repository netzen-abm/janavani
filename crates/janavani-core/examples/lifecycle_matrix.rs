use janavani_core::CaseStatus;

fn main() {
    use CaseStatus::*;
    let statuses = [Draft, Review, Ready, Submitting, Queued, Submitted, Acknowledged,
        FollowUp, InProgress, Responded, Resolved, Escalated, Closed, Archived];
    let mut out = String::from("{");
    for (i, current) in statuses.iter().enumerate() {
        if i > 0 { out.push(','); }
        out.push_str(&format!("\"{}\":[", serde_json::to_string(current).unwrap().trim_matches('"')));
        let mut first = true;
        for target in statuses.iter() {
            if current.can_transition(*target) {
                if !first { out.push(','); }
                first = false;
                out.push_str(&serde_json::to_string(target).unwrap());
            }
        }
        out.push(']');
    }
    out.push('}');
    println!("{out}");
}

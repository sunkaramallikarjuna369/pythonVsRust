// Null handling: a missing value is wrapped in an Option that must be
// opened (match / map / unwrap_or) before it can be used.
// Matches section 6 (PART C).
use std::collections::HashMap;

struct User {
    fields: HashMap<&'static str, String>,
}

fn lowercase_all(users: &[User]) -> Vec<String> {
    users
        .iter()
        .map(|user| {
            let email: Option<&String> = user.fields.get("email");
            // Compiler forces us to handle the None case - no build otherwise.
            match email {
                Some(value) => value.to_lowercase(),
                None => String::new(),
            }
        })
        .collect()
}

fn main() {
    let mut users: Vec<User> = (0..99_999)
        .map(|i| {
            let mut fields = HashMap::new();
            fields.insert("email", format!("user{i}@example.com"));
            User { fields }
        })
        .collect();
    users.push(User { fields: HashMap::new() }); // one record with no email

    let result = lowercase_all(&users);
    println!("safe run handled all {} records, no crash possible", result.len());
}

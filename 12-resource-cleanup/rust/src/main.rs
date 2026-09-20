// Resource cleanup: when the owner leaves scope, Drop runs
// automatically and closes the file. Always, at a known moment.
// Matches section 12 (PART C).
use std::fs::File;
use std::io::Write;

fn write_scoped(path: &str) -> std::io::Result<()> {
    let mut f = File::create(path)?;
    f.write_all(b"closed the instant this function returns\n")?;
    Ok(())
    // `f` goes out of scope here -> Drop closes the file, guaranteed.
}

fn main() -> std::io::Result<()> {
    let dir = std::env::temp_dir();
    let path = dir.join("rust_resource_cleanup.txt");
    let path_str = path.to_string_lossy().to_string();

    write_scoped(&path_str)?;
    println!("file closed automatically at end of scope -> {path_str}");
    Ok(())
}

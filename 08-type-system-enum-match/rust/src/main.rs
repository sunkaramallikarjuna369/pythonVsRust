// Type system (enum + match): match must cover every variant, or the
// program does not compile. Illegal/forgotten states can't be built.
// Matches section 8 (PART C).
use std::time::Instant;

enum Shape {
    Circle { r: f64 },
    Rect { w: f64, h: f64 },
    Triangle { b: f64, h: f64 },
}

fn area(shape: &Shape) -> f64 {
    match shape {
        Shape::Circle { r } => std::f64::consts::PI * r * r,
        Shape::Rect { w, h } => w * h,
        Shape::Triangle { b, h } => 0.5 * b * h,
        // Adding a new variant to `Shape` without a new arm here is a
        // compile error - the bug is caught before the program exists.
    }
}

fn main() {
    let mut shapes = Vec::with_capacity(5_000_000);
    shapes.extend((0..2_000_000).map(|_| Shape::Circle { r: 2.0 }));
    shapes.extend((0..2_000_000).map(|_| Shape::Rect { w: 3.0, h: 4.0 }));
    shapes.extend((0..1_000_000).map(|_| Shape::Triangle { b: 3.0, h: 4.0 }));

    let start = Instant::now();
    let total: f64 = shapes.iter().map(area).sum();
    let elapsed = start.elapsed();
    println!("total area={total:.1}");
    println!("elapsed: {:.3}s", elapsed.as_secs_f64());
}

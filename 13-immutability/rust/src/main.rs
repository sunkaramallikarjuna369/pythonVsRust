// Immutability: `let` is locked by default; `let mut` opts in to
// change, and only ONE &mut may exist at a time.
// Matches section 13 (PART C).

fn main() {
    let x = vec![1, 2, 3]; // immutable by default

    // x.push(4); // <-- compile error: "cannot borrow `x` as mutable"
    //               unless declared `let mut x = vec![1, 2, 3];`

    let mut y = x.clone(); // opt in explicitly
    y.push(4);
    println!("x (locked):   {x:?}");
    println!("y (let mut):  {y:?}");

    // Only one mutable borrow at a time - the compiler rejects aliased
    // writers, so "who changed this?" bugs are caught before running.
    mutate_in_place(&mut y);
    println!("y after &mut fn call: {y:?}");
}

fn mutate_in_place(values: &mut Vec<i32>) {
    values.push(999); // explicit: the signature says this can mutate
}

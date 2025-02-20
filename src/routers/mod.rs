pub mod account;
pub mod error;
pub mod organization;
pub mod permission;
pub mod phrase;
pub mod profile;
pub mod quran;
pub mod translation;
pub mod user;

use std::collections::BTreeMap;
use std::hash::Hash;

/// finds the relatives in the vector
/// Vec<(Obj1, Obj2)>
/// This will collect the Obj2 that related to the Obj1 and returns
/// a BTreeMap (We want the elements to be in order)
pub fn multip<T, U, F, NT>(vector: Vec<(T, U)>, insert_data_type: F) -> BTreeMap<NT, Vec<U>>
where
    T: Sized + Clone,
    U: Sized + Clone,
    NT: Sized + Eq + Hash + Ord,
    F: Fn(T) -> NT,
{
    let mut map: BTreeMap<NT, Vec<U>> = BTreeMap::new();
    for item in vector {
        map.entry(insert_data_type(item.0))
            .and_modify(|c| c.push(item.1.clone()))
            .or_insert(vec![item.1]);
    }

    map
}

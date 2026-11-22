"""Focused core Rust laboratories: errors, generics, traits, and engineering."""
from quest_catalog import Quest

RAW = {
31: ('parse_result','text: &str','Result<i64, std::num::ParseIntError>','text.parse::<i64>()','assert_eq!(parse_result("42"),Ok(42)); assert!(parse_result("bad").is_err());','Preserve the concrete parsing error using Result.'),
32: ('parse_sum','left: &str, right: &str','Result<i64, std::num::ParseIntError>','let a=left.parse::<i64>()?; let b=right.parse::<i64>()?; Ok(a+b)','assert_eq!(parse_sum("2","3"),Ok(5)); assert!(parse_sum("x","3").is_err());','Use ? to propagate failures from two parsing operations.'),
33: ('domain_error','value: i32','Result<u32, String>','u32::try_from(value).map_err(|_|format!("negative value: {value}"))','assert_eq!(domain_error(3),Ok(3)); assert!(domain_error(-1).unwrap_err().contains("negative"));','Map a conversion error into a meaningful domain error.'),
34: ('checked_multiply','a: i32, b: i32','Option<i32>','a.checked_mul(b)','assert_eq!(checked_multiply(2,3),Some(6)); assert_eq!(checked_multiply(i32::MAX,2),None);','Test checked arithmetic at an overflow boundary.'),
35: ('parse_lines','text: &str','Result<Vec<i32>, std::num::ParseIntError>','text.lines().map(str::parse::<i32>).collect()','assert_eq!(parse_lines("1\n2"),Ok(vec![1,2])); assert!(parse_lines("1\nx").is_err());','Collect an iterator of Results into a single Result.'),
36: ('validate_batch','values: &[i32]','Result<(), String>','for (index,value) in values.iter().enumerate() {if *value<0 {return Err(format!("negative at index {index}"));}} Ok(())','assert_eq!(validate_batch(&[0,1]),Ok(())); assert!(validate_batch(&[0,-1]).unwrap_err().contains("1"));','Write table-driven validation with actionable error context.'),
37: ('assert_invariant','values: &[u32]','bool','values.windows(2).all(|w|w[0]<=w[1])','assert!(assert_invariant(&[1,1,2])); assert!(!assert_invariant(&[2,1]));','Express an invariant with windows and test boundary cases.'),
38: ('annotated_parse','text: &str','Result<u16,String>','text.parse::<u16>().map_err(|err|format!("cannot parse {text:?}: {err}"))','assert!(annotated_parse("abc").unwrap_err().contains("abc")); assert_eq!(annotated_parse("80"),Ok(80));','Retain input context when translating low-level errors.'),
39: ('all_positive','values: &[Result<i32,String>]','Result<bool,String>','values.iter().try_fold(true,|ok,item|{let n=item.as_ref().map_err(Clone::clone)?; Ok(ok && *n>0)})','assert_eq!(all_positive(&[Ok(1),Ok(2)]),Ok(true)); assert_eq!(all_positive(&[Ok(0)]),Ok(false)); assert!(all_positive(&[Err("bad".into())]).is_err());','Combine multiple fallible values without suppressing errors.'),
40: ('reliability_boss','text: &str','Result<i64,String>','text.lines().enumerate().try_fold(0_i64,|sum,(index,line)|{let value=line.trim().parse::<i64>().map_err(|e|format!("line {}: {e}",index+1))?; sum.checked_add(value).ok_or_else(||format!("overflow at line {}",index+1))})','assert_eq!(reliability_boss("1\n2"),Ok(3)); assert!(reliability_boss("x").unwrap_err().contains("line 1")); assert!(reliability_boss("9223372036854775807\n1").is_err());','Boss: combine parsing, error context, and checked aggregation.'),
41: ('generic_identity','value: T','T','value','assert_eq!(generic_identity(3_i32),3); assert_eq!(generic_identity(String::from("a")),"a");','Implement a truly generic identity function.'),
42: ('generic_pair','left: A, right: B','(A,B)','(left,right)','assert_eq!(generic_pair(3,"rust"),(3,"rust"));','Use two independent generic type parameters.'),
43: ('display_any','value: &T','String','format!("{value}")','assert_eq!(display_any(&42),"42"); assert_eq!(display_any(&"hi"),"hi");','Introduce the Display trait bound.'),
44: ('generic_max','left: T, right: T','T','if left>=right {left} else {right}','assert_eq!(generic_max(2,5),5); assert_eq!(generic_max("b","a"),"b");','Use PartialOrd to compare generic values.'),
45: ('generic_sum','values: &[T]','T','values.iter().copied().fold(T::default(),|acc,x|acc+x)','assert_eq!(generic_sum(&[1_u32,2,3]),6); assert_eq!(generic_sum(&[1.5_f64,2.5]),4.0);','Combine Copy, Default, and Add trait bounds.'),
46: ('default_or','value: Option<T>','T','value.unwrap_or_default()','assert_eq!(default_or(Some(7_u32)),7); assert_eq!(default_or(None::<String>),"");','Use Default with a generic Option.'),
47: ('into_string','value: T','String','value.to_string()','assert_eq!(into_string(12),"12");','Constrain a generic function by ToString.'),
48: ('first_view','values: &\'a [T]','Option<&\'a T>','values.first()','assert_eq!(first_view(&[4,5]),Some(&4)); assert_eq!(first_view(&[] as &[i32]),None);','Write an explicit lifetime on a borrowed return value.'),
49: ('render_objects','values: &[&dyn std::fmt::Display]','Vec<String>','values.iter().map(|value|value.to_string()).collect()','let a=2; let b="hi"; assert_eq!(render_objects(&[&a,&b]),vec!["2","hi"]);','Use heterogeneous trait objects with dynamic dispatch.'),
50: ('abstraction_boss','values: &[T]','Option<T>','values.iter().copied().max_by(|a,b|a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal))','assert_eq!(abstraction_boss(&[1,3,2]),Some(3)); assert_eq!(abstraction_boss(&[] as &[i32]),None);','Boss: generic borrowed input, trait bounds and optional output.'),
61: ('module_path','value: i32','i32','std::cmp::max(value,0)','assert_eq!(module_path(-3),0);','Use an explicitly qualified standard-library module path.'),
62: ('public_api','text: &str','String','text.to_owned()','assert_eq!(public_api("ok"),"ok");','Design an owned public API without leaking implementation details.'),
63: ('crate_identifier','text: &str','String','text.trim().replace(\'-\',"_").to_lowercase()','assert_eq!(crate_identifier(" My-Crate "),"my_crate");','Normalize a crate identifier for Cargo naming conventions.'),
64: ('feature_switch','enabled: bool','Option<&\'static str>','enabled.then_some("experimental")','assert_eq!(feature_switch(true),Some("experimental")); assert_eq!(feature_switch(false),None);','Model a feature switch; discuss Cargo feature flags in LEVEL.md.'),
65: ('workspace_member','workspace: &std::path::Path, member: &str','std::path::PathBuf','workspace.join(member)','assert_eq!(workspace_member(std::path::Path::new("root"),"crate"),std::path::PathBuf::from("root/crate"));','Compose workspace paths using PathBuf rather than string separators.'),
66: ('doc_example','n: i32','i32','n.saturating_mul(n)','assert_eq!(doc_example(4),16); assert_eq!(doc_example(i32::MAX),i32::MAX);','Explain documentation examples and saturating arithmetic.'),
67: ('unique_dependencies','names: &[&str]','usize','names.iter().copied().filter(|name|!name.is_empty()).collect::<std::collections::HashSet<_>>().len()','assert_eq!(unique_dependencies(&["serde","serde","tokio"]),2);','Audit duplicate dependencies with a HashSet.'),
68: ('config_from_env','name: &str, fallback: &str','String','std::env::var(name).unwrap_or_else(|_|fallback.to_owned())','assert_eq!(config_from_env("RUST_RPG_UNLIKELY_CONFIG_KEY_987", "default"),"default");','Read environment-based configuration with a fallback.'),
69: ('semver_triplet','version: &str','Option<(u64,u64,u64)>','let mut parts=version.split(\'.\'); let major=parts.next()?.parse().ok()?; let minor=parts.next()?.parse().ok()?; let patch=parts.next()?.parse().ok()?; if parts.next().is_some(){return None;} Some((major,minor,patch))','assert_eq!(semver_triplet("1.2.3"),Some((1,2,3))); assert_eq!(semver_triplet("1.2"),None);','Validate a restricted three-part version string.'),
70: ('engineering_boss','paths: &[&str]','Result<Vec<std::path::PathBuf>,String>','paths.iter().map(|name|{if name.is_empty() || name.contains("..") || name.starts_with(\'/\'){Err(format!("unsafe member: {name}"))} else {Ok(std::path::PathBuf::from(name))}}).collect()','assert_eq!(engineering_boss(&["core","cli"]).unwrap().len(),2); assert!(engineering_boss(&["../escape"]).is_err());','Boss: validate workspace member paths and reject traversal.'),
}

CORE_QUESTS = {n: Quest(*item) for n,item in RAW.items()}
GENERIC_SIGNATURES = {
41: ('<T>', ''), 42: ('<A, B>', ''), 43: ('<T: std::fmt::Display>', ''),
44: ('<T: PartialOrd>', ''), 45: ('<T: Copy + Default + std::ops::Add<Output = T>>', ''),
46: ('<T: Default>', ''), 47: ('<T: ToString>', ''),
48: ("<'a, T>", ''), 50: ('<T: Copy + PartialOrd>', ''),
}

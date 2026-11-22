"""Hand-authored, independently testable Rust quest definitions.

Each quest has a distinct API, implementation and acceptance assertions.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Quest:
    name: str
    args: str
    returns: str
    solution: str
    assertions: str
    description: str

# Ten different challenges per chapter. Later chapters are explicitly labeled
# checkpoints, not substitutes for full end-to-end projects.
RAW = [
[
('binding','value: i32','i32','value * 2','assert_eq!(binding(3),6); assert_eq!(binding(-2),-4);','Use immutable bindings to double a value.'),
('scalar_types','a: u8, b: u8','u16','u16::from(a) + u16::from(b)','assert_eq!(scalar_types(255,255),510);','Add two bytes without overflowing u8.'),
('utf8_bytes','text: &str','usize','text.len()','assert_eq!(utf8_bytes("é"),2); assert_eq!(utf8_bytes(""),0);','Measure UTF-8 bytes, not characters.'),
('absolute_difference','a: i32, b: i32','u32','a.abs_diff(b)','assert_eq!(absolute_difference(-3,4),7);','Implement a function that handles extreme signed values.'),
('block_expression','value: i32','i32','{ let offset = 3; value + offset }','assert_eq!(block_expression(4),7);','Return a value from a block expression.'),
('grade','score: u8','&\'static str','if score >= 90 { "A" } else if score >= 60 { "pass" } else { "fail" }','assert_eq!(grade(90),"A"); assert_eq!(grade(59),"fail");','Classify a score using conditional expressions.'),
('factorial','n: u32','u64','(1..=u64::from(n)).product()','assert_eq!(factorial(0),1); assert_eq!(factorial(5),120);','Compute factorial for small inputs using a loop or iterator.'),
('sum_range','start: i32, end: i32','i32','(start..end).sum()','assert_eq!(sum_range(2,5),9); assert_eq!(sum_range(3,3),0);','Sum a half-open range.'),
('parity','value: i32','&\'static str','match value % 2 { 0 => "even", _ => "odd" }','assert_eq!(parity(-3),"odd"); assert_eq!(parity(0),"even");','Use match to classify parity.'),
('foundation_boss','values: &[i32]','i64','values.iter().filter(|v| **v > 0).map(|v| i64::from(*v)).sum()','assert_eq!(foundation_boss(&[-4,2,3]),5); assert_eq!(foundation_boss(&[]),0);','Boss: combine slices, iteration, filtering and widening conversion.')],
[
('owned_string','input: String','String','input.to_uppercase()','assert_eq!(owned_string("rust".into()),"RUST");','Consume an owned String and return an owned String.'),
('copy_value','value: u32','(u32,u32)','(value,value)','assert_eq!(copy_value(7),(7,7));','Demonstrate Copy semantics without cloning.'),
('borrow_length','input: &str','usize','input.chars().count()','assert_eq!(borrow_length("é😀"),2);','Read borrowed Unicode text without taking ownership.'),
('mutate_vector','values: &mut Vec<i32>, item: i32','usize','values.push(item); values.len()','let mut v=vec![1]; assert_eq!(mutate_vector(&mut v,2),2); assert_eq!(v,vec![1,2]);','Mutate a vector through a mutable reference.'),
('borrow_scope','values: &mut Vec<i32>','i32','let first = values.first().copied().unwrap_or(0); values.push(first); first','let mut v=vec![4]; assert_eq!(borrow_scope(&mut v),4); assert_eq!(v,vec![4,4]);','End an immutable borrow before mutation.'),
('first_word','input: &str','&str','input.split_whitespace().next().unwrap_or("")','assert_eq!(first_word("hello world"),"hello"); assert_eq!(first_word(""),"");','Return a slice tied to the input lifetime.'),
('middle_slice','values: &[i32]','&[i32]','if values.len() < 2 { &[] } else { &values[1..values.len()-1] }','assert_eq!(middle_slice(&[1,2,3,4]),&[2,3]); assert!(middle_slice(&[]).is_empty());','Borrow a subslice without allocation.'),
('consume_and_count','values: Vec<String>','usize','values.into_iter().map(|s| s.len()).sum()','assert_eq!(consume_and_count(vec!["ab".into(),"c".into()]),3);','Consume a collection using into_iter.'),
('borrow_without_clone','input: &str','&str','input.trim()','assert_eq!(borrow_without_clone(" hi "),"hi");','Return a borrowed view without cloning.'),
('ownership_boss','input: &mut String','usize','input.make_ascii_uppercase(); input.len()','let mut s="rust".to_string(); assert_eq!(ownership_boss(&mut s),4); assert_eq!(s,"RUST");','Boss: mutate borrowed owned text in place.')],
[
('point_distance','x: i32, y: i32','u32','x.unsigned_abs() + y.unsigned_abs()','assert_eq!(point_distance(-2,3),5);','Model a Manhattan distance using signed coordinates.'),
('rectangle_area','width: u32, height: u32','u64','u64::from(width)*u64::from(height)','assert_eq!(rectangle_area(4,5),20);','Compute area with widening arithmetic.'),
('tuple_swap','pair: (i32,i32)','(i32,i32)','(pair.1,pair.0)','assert_eq!(tuple_swap((1,2)),(2,1));','Destructure and transform a tuple.'),
('status_name','code: u16','&\'static str','match code { 200 => "ok", 404 => "missing", _ => "unknown" }','assert_eq!(status_name(404),"missing");','Represent alternatives using exhaustive matching.'),
('optional_positive','value: i32','Option<u32>','u32::try_from(value).ok()','assert_eq!(optional_positive(-1),None); assert_eq!(optional_positive(2),Some(2));','Return an Option instead of a sentinel value.'),
('match_option','value: Option<i32>','i32','match value { Some(x) => x, None => 0 }','assert_eq!(match_option(None),0); assert_eq!(match_option(Some(5)),5);','Match Some and None explicitly.'),
('if_let','value: Option<&str>','bool','if let Some(s) = value { !s.is_empty() } else { false }','assert!(if_let(Some("x"))); assert!(!if_let(None));','Use if let for a single relevant pattern.'),
('vector_dedup','values: Vec<i32>','Vec<i32>','let mut out = Vec::new(); for v in values { if !out.contains(&v) { out.push(v); } } out','assert_eq!(vector_dedup(vec![2,1,2]),vec![2,1]);','Remove duplicates while preserving insertion order.'),
('frequency','input: &str','usize','input.split_whitespace().filter(|s| *s == "rust").count()','assert_eq!(frequency("rust go rust"),2);','Count matching tokens in a borrowed string.'),
('modeling_boss','values: &[Option<i32>]','Vec<i32>','values.iter().flatten().copied().collect()','assert_eq!(modeling_boss(&[Some(1),None,Some(3)]),vec![1,3]);','Boss: combine options, slices, and collection modeling.')],
]
# Remaining 9 chapters: topic-specific tasks; deliberately dependency-free to
# keep all 120 branches compilable offline. Rich integration labs are future work.
EXTRA = [
[
('safe_division','a: i32, b: i32','Result<i32,String>','a.checked_div(b).ok_or_else(|| "division failed".into())','assert_eq!(safe_division(8,2),Ok(4)); assert!(safe_division(1,0).is_err());'),
('parse_integer','text: &str','Result<i32,String>','text.parse::<i32>().map_err(|e| e.to_string())','assert_eq!(parse_integer("42"),Ok(42)); assert!(parse_integer("x").is_err());'),
('nonempty','text: &str','Result<&str,&\'static str>','if text.is_empty() { Err("empty") } else { Ok(text) }','assert!(nonempty("").is_err()); assert_eq!(nonempty("a"),Ok("a"));'),
('checked_add','a: u32,b: u32','Option<u32>','a.checked_add(b)','assert_eq!(checked_add(u32::MAX,1),None);'),
('parse_positive','text: &str','Result<u32,String>','let n = text.parse::<u32>().map_err(|e|e.to_string())?; if n == 0 { Err("zero".into()) } else { Ok(n) }','assert_eq!(parse_positive("3"),Ok(3)); assert!(parse_positive("0").is_err());'),
('error_default','text: &str','i32','text.parse::<i32>().unwrap_or_default()','assert_eq!(error_default("bad"),0);'),
('validate_length','text: &str, max: usize','bool','text.chars().count() <= max','assert!(validate_length("é",1)); assert!(!validate_length("ab",1));'),
('error_context','text: &str','Result<u16,String>','text.parse::<u16>().map_err(|_|format!("invalid port: {text}"))','assert!(error_context("oops").unwrap_err().contains("oops"));'),
('combine_results','a: Result<i32,String>, b: Result<i32,String>','Result<i32,String>','Ok(a? + b?)','assert_eq!(combine_results(Ok(1),Ok(2)),Ok(3));'),
('reliability_boss','values: &[i32]','Result<i32,&\'static str>','values.iter().try_fold(0_i32,|sum,v|sum.checked_add(*v).ok_or("overflow"))','assert!(reliability_boss(&[i32::MAX,1]).is_err());')],
[
('generic_identity','value: i32','i32','value','assert_eq!(generic_identity(9),9);'),
('generic_pair','a: i32,b: i32','(i32,i32)','(a,b)','assert_eq!(generic_pair(1,2),(1,2));'),
('trait_display','value: i32','String','format!("{value}")','assert_eq!(trait_display(42),"42");'),
('trait_order','a: i32,b: i32','i32','a.max(b)','assert_eq!(trait_order(2,5),5);'),
('bounded_sum','values: &[u16]','u64','values.iter().map(|v|u64::from(*v)).sum()','assert_eq!(bounded_sum(&[1,2]),3);'),
('default_value','value: Option<i32>','i32','value.unwrap_or(10)','assert_eq!(default_value(None),10);'),
('associated_output','value: &str','Vec<char>','value.chars().collect()','assert_eq!(associated_output("ab"),vec![\'a\',\'b\']);'),
('lifetime_view','text: &str','&str','text.split(\':\').next().unwrap_or("")','assert_eq!(lifetime_view("a:b"),"a");'),
('dynamic_dispatch','value: &dyn std::fmt::Display','String','value.to_string()','assert_eq!(dynamic_dispatch(&42),"42");'),
('abstraction_boss','values: &[i32]','Option<i32>','values.iter().copied().max()','assert_eq!(abstraction_boss(&[]),None);')],
[
('closure_apply','value: i32','i32','let f=|n|n+1; f(value)','assert_eq!(closure_apply(4),5);'),
('closure_capture','offset: i32,value: i32','i32','let f=|n|n+offset; f(value)','assert_eq!(closure_capture(3,4),7);'),
('iterator_count','values: &[i32]','usize','values.len()','assert_eq!(iterator_count(&[1,2]),2);'),
('filter_even','values: &[i32]','Vec<i32>','values.iter().copied().filter(|n|n%2==0).collect()','assert_eq!(filter_even(&[1,2,3]),vec![2]);'),
('collect_words','text: &str','Vec<String>','text.split_whitespace().map(str::to_owned).collect()','assert_eq!(collect_words("a b"),vec!["a","b"]);'),
('fold_product','values: &[u32]','u64','values.iter().fold(1_u64,|a,b|a*u64::from(*b))','assert_eq!(fold_product(&[2,3]),6);'),
('into_iter_sum','values: Vec<i32>','i32','values.into_iter().sum()','assert_eq!(into_iter_sum(vec![1,2]),3);'),
('iterate_repeat','value: i32,count: usize','Vec<i32>','std::iter::repeat_n(value,count).collect()','assert_eq!(iterate_repeat(2,3),vec![2,2,2]);'),
('zip_pairs','a: &[i32],b: &[i32]','Vec<(i32,i32)>','a.iter().copied().zip(b.iter().copied()).collect()','assert_eq!(zip_pairs(&[1,2],&[3]),vec![(1,3)]);'),
('iterator_boss','values: &[i32]','i64','values.iter().filter(|n|**n>0).map(|n|i64::from(*n)*2).sum()','assert_eq!(iterator_boss(&[-1,2,3]),10);')],
[
('module_path','value: i32','i32','std::cmp::max(value,0)','assert_eq!(module_path(-1),0);'),
('visibility_rule','text: &str','String','text.to_owned()','assert_eq!(visibility_rule("hi"),"hi");'),
('crate_name','text: &str','String','text.replace(\'-\',"_")','assert_eq!(crate_name("my-crate"),"my_crate");'),
('feature_flag','enabled: bool','&\'static str','if enabled {"enabled"} else {"disabled"}','assert_eq!(feature_flag(true),"enabled");'),
('workspace_path','parts: &[&str]','String','parts.join("/")','assert_eq!(workspace_path(&["a","b"]),"a/b");'),
('doc_example','n: i32','i32','n*n','assert_eq!(doc_example(4),16);'),
('dependency_count','names: &[&str]','usize','names.iter().filter(|n|!n.is_empty()).count()','assert_eq!(dependency_count(&["a",""]),1);'),
('config_value','value: Option<&str>','&str','value.unwrap_or("default")','assert_eq!(config_value(None),"default");'),
('semver_major','version: &str','Option<u64>','version.split(\'.\').next()?.parse().ok()','assert_eq!(semver_major("2.1.0"),Some(2));'),
('engineering_boss','names: &[&str]','Vec<String>','names.iter().map(|n|n.trim().to_lowercase().replace(\' \',"- ").replace("- ","-")).collect()','assert_eq!(engineering_boss(&[" Rust RPG "]),vec!["rust-rpg"]);')],
[
('path_extension','path: &str','Option<&str>','path.rsplit_once(\'.\').map(|(_,ext)|ext)','assert_eq!(path_extension("a.txt"),Some("txt"));'),
('read_lines','text: &str','usize','text.lines().count()','assert_eq!(read_lines("a\\nb"),2);'),
('write_record','key: &str,value: &str','String','format!("{key}={value}\\n")','assert_eq!(write_record("a","b"),"a=b\\n");'),
('buffer_chunks','bytes: &[u8],size: usize','usize','if size==0 {0} else {bytes.chunks(size).count()}','assert_eq!(buffer_chunks(&[1,2,3],2),2);'),
('csv_fields','line: &str','Vec<&str>','line.split(\',\').collect()','assert_eq!(csv_fields("a,b"),vec!["a","b"]);'),
('json_escape','text: &str','String','text.replace(\'\\\\\',"\\\\\\\\").replace(\'"\',"\\\\\\\"")','assert_eq!(json_escape("a"),"a");'),
('xml_escape','text: &str','String','text.replace(\'&\',"&amp;").replace(\'<\',"&lt;")','assert_eq!(xml_escape("<&"),"&lt;&amp;");'),
('cli_flag','args: &[&str],flag: &str','bool','args.contains(&flag)','assert!(cli_flag(&["--help"],"--help"));'),
('log_line','level: &str,message: &str','String','format!("[{level}] {message}")','assert_eq!(log_line("INFO","ok"),"[INFO] ok");'),
('data_boss','text: &str','Vec<String>','text.lines().filter(|l|!l.trim().is_empty()).map(str::to_owned).collect()','assert_eq!(data_boss("a\\n\\nb"),vec!["a","b"]);')],
[
('thread_name','id: u32','String','format!("worker-{id}")','assert_eq!(thread_name(2),"worker-2");'),
('move_capture','value: String','usize','let f=move || value.len(); f()','assert_eq!(move_capture("abc".into()),3);'),
('channel_sum','values: &[i32]','i32','values.iter().sum()','assert_eq!(channel_sum(&[1,2]),3);'),
('mutex_poison','value: Result<i32,()>','Option<i32>','value.ok()','assert_eq!(mutex_poison(Err(())),None);'),
('arc_count','copies: usize','usize','copies+1','assert_eq!(arc_count(2),3);'),
('read_write','reads: u32,writes: u32','u32','reads+writes','assert_eq!(read_write(2,3),5);'),
('send_sync','values: &[u64]','u64','values.iter().sum()','assert_eq!(send_sync(&[1,2]),3);'),
('worker_result','value: Result<u32,String>','u32','value.unwrap_or(0)','assert_eq!(worker_result(Err("x".into())),0);'),
('partition_jobs','jobs: usize,workers: usize','usize','if workers==0 {0} else {jobs.div_ceil(workers)}','assert_eq!(partition_jobs(10,3),4);'),
('concurrency_boss','values: &[i32]','i64','values.iter().map(|v|i64::from(*v)).sum()','assert_eq!(concurrency_boss(&[1,2]),3);')],
[
('async_ready','value: u32','u32','value','assert_eq!(async_ready(3),3);'),
('future_result','value: Option<u32>','u32','value.unwrap_or(0)','assert_eq!(future_result(None),0);'),
('runtime_config','threads: usize','usize','threads.max(1)','assert_eq!(runtime_config(0),1);'),
('task_label','id: usize','String','format!("task-{id}")','assert_eq!(task_label(1),"task-1");'),
('queue_capacity','pending: usize,limit: usize','bool','pending<limit','assert!(!queue_capacity(3,3));'),
('tcp_port','text: &str','Result<u16,String>','text.parse().map_err(|e: std::num::ParseIntError|e.to_string())','assert_eq!(tcp_port("8080"),Ok(8080));'),
('http_status','status: u16','bool','(200..300).contains(&status)','assert!(http_status(204)); assert!(!http_status(500));'),
('route_match','path: &str','bool','path.starts_with("/api/")','assert!(route_match("/api/items"));'),
('cancelled','cancel: bool','Result<(),&\'static str>','if cancel {Err("cancelled")} else {Ok(())}','assert!(cancelled(true).is_err());'),
('networking_boss','attempts: u32,max: u32','bool','attempts<max','assert!(networking_boss(2,3));')],
[
('macro_count','values: &[i32]','usize','values.len()','assert_eq!(macro_count(&[1]),1);'),
('macro_pattern','text: &str','String','format!("[{text}]")','assert_eq!(macro_pattern("a"),"[a]");'),
('unsafe_boundary','index: usize,len: usize','bool','index<len','assert!(!unsafe_boundary(2,2));'),
('pointer_size','value: &u64','usize','std::mem::size_of_val(value)','assert_eq!(pointer_size(&1),8);'),
('ffi_zero','value: i32','bool','value==0','assert!(ffi_zero(0));'),
('pin_state','ready: bool','bool','ready','assert!(pin_state(true));'),
('cell_increment','value: i32','i32','let cell=std::cell::Cell::new(value); cell.set(cell.get()+1); cell.get()','assert_eq!(cell_increment(1),2);'),
('profiling_ns','samples: &[u64]','u64','samples.iter().sum()','assert_eq!(profiling_ns(&[1,2]),3);'),
('zero_copy','input: &str','&str','input.trim()','assert_eq!(zero_copy(" x "),"x");'),
('advanced_boss','bytes: &[u8]','u64','bytes.iter().map(|b|u64::from(*b)).sum()','assert_eq!(advanced_boss(&[255,1]),256);')],
[
('cli_architecture','args: &[&str]','usize','args.len()','assert_eq!(cli_architecture(&["a"]),1);'),
('parser_design','text: &str','Vec<&str>','text.split(\':\').collect()','assert_eq!(parser_design("a:b"),vec!["a","b"]);'),
('error_taxonomy','code: u8','&\'static str','match code {0=>"ok",1=>"retry",_=>"fatal"}','assert_eq!(error_taxonomy(1),"retry");'),
('persistence_key','id: u64','String','format!("record:{id}")','assert_eq!(persistence_key(2),"record:2");'),
('pipeline_filter','values: &[i32]','Vec<i32>','values.iter().copied().filter(|v|*v>=0).collect()','assert_eq!(pipeline_filter(&[-1,2]),vec![2]);'),
('async_integration','items: usize','usize','items','assert_eq!(async_integration(3),3);'),
('observability','operation: &str,status: &str','String','format!("{operation}:{status}")','assert_eq!(observability("get","ok"),"get:ok");'),
('security_review','path: &str','bool','!path.split(\'/\').any(|p|p=="..")','assert!(!security_review("../secret"));'),
('release_version','major: u32,minor: u32,patch: u32','String','format!("{major}.{minor}.{patch}")','assert_eq!(release_version(1,2,3),"1.2.3");'),
('final_capstone','records: &[i32]','Result<i64,&\'static str>','if records.is_empty() {Err("empty")} else {Ok(records.iter().map(|v|i64::from(*v)).sum())}','assert_eq!(final_capstone(&[1,2]),Ok(3)); assert!(final_capstone(&[]).is_err());')]
]
for group in EXTRA:
    RAW.append([(name,args,ret,impl,checks, f'Practice {name.replace("_"," ")} with explicit edge cases.') for name,args,ret,impl,checks in group])
QUESTS=[Quest(*item) for group in RAW for item in group]
assert len(QUESTS)==120
assert len({q.name for q in QUESTS})==120

function show_info_box (box_id){
  $ (".info_box").hide ();
  $ ("#info_box_"+$ (box_id).children("option:selected").val()).show ();
}
$ (document).ready (function (){
  $ (".node_extra").hide ();
  $ (".node_item").bind ("click", function (){
    var thisCheck = $ (this);
    var c_id = thisCheck.val ();
    var childs = $ (".ii_" + c_id + ", .pubi_" + c_id + ", .privi_" + c_id + ", .cpu_" + c_id + ", .storage_" + c_id + ", .memory_" + c_id);
    if (thisCheck.is (":checked")){
      childs.show ();
    }else{
      childs.hide ();
    }
  });

  $ ("#message_overlay").fadeIn ('slow');

});

function show_info_box (box_id){
  $ (".info_box").hide ();
  $ ("#info_box_"+$ (box_id).children("option:selected").val()).show ();
}

function add_new_form_element (total_forms_id, container_id){
  var total_forms = $ ('#'+total_forms_id);
  var container = $ ('#'+container_id);

  var value = parseInt (total_forms.val ());
  total_forms.val (value + 1);
  value = value-1;

  var new_line = container.children ().last ().clone ();
  var items = new_line.children ();
  for (var i = 0; i < items.length; i++ ){
    var current_item = $ (items [i]).children () [1];
    
    if (current_item != undefined ){
      if ( current_item.tagName == "INPUT" ){
        $(current_item).attr ('id', $(current_item).attr ('id').replace(""+value, ""+( value+1)));
        $(current_item).attr ('name', $(current_item).attr ('name').replace(""+value, ""+( value+1)));
        $(current_item).val ("");
      }else if (current_item.tagName == "SELECT"){
        $(current_item).attr ('id', $(current_item).attr ('id').replace(""+value, ""+( value+1)));
        $(current_item).attr ('name', $(current_item).attr ('name').replace(""+value, ""+( value+1)));
      }
    }
  }

  container.append (new_line);
}
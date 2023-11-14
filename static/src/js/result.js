function year_clicked(year_id) {
    $("#ue_section").load('/load_ue_section_by_year/'+year_id)
}

function show_result(year_id, session, ue_id) {
    console.log(year_id, session, ue_id)
}
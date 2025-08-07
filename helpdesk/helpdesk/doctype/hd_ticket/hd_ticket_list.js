frappe.listview_settings["HD Ticket"] = {
  onload(listview) {
    // Agregar campo al header de filtros (parte superior)
    listview.page.add_field({
      label: "xxxxxxxxxxxxxx",
      fieldtype: "DateRange",
      fieldname: "creation_range",
      change() {
        const value = this.get_value(); // [desde, hasta]
        if (value && value[0] && value[1]) {
          // Eliminar filtro anterior si existe
          listview.filter_area.remove("creation");

          // Agregar filtro por rango
          listview.filter_area.add([
            "HD Ticket",
            "creation",
            "between",
            [value[0], value[1]],
          ]);
        }
      },
    });
  },
};

// frappe.listview_settings["HD Ticket"] = {

//   refresh: function (listview) {
//     $(".layout-side-section").hide();
//   },
// };

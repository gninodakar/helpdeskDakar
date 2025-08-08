frappe.listview_settings["HD Ticket"] = {
  refresh(listview) {
    
  },
  onload(listview) {
    // Add field to filter header (top)
    $(".layout-side-section").hide();
    listview.page.add_field({
      label: "Date Range",
      fieldtype: "DateRange",
      fieldname: "creation_range",
      change() {
        const value = this.get_value(); // [from , to]
        if (value && value[0] && value[1]) {
          // remove creation filter
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

// Collapse (not remove) the sidebar everywhere

(function () {
  function collapseSidebar(page) {
    if (!page?.sidebar) return;
    // Run after render so the element exists
    setTimeout(() => {
      // Collapse only if currently shown
      if (page.sidebar.is(':visible')) {
        page.sidebar.toggle(false); // false = collapsed
      }
    }, 50);
  }

  // 1) All LIST VIEWS
  frappe.listview_settings["*"] = {
    onload(listview) {
      collapseSidebar(listview?.page);
    },
    refresh(listview) {
      collapseSidebar(listview?.page);
    },
  };

  // 2) All FORM VIEWS
  frappe.ui.form.on("*", {
    onload(frm) {
      collapseSidebar(frm?.page);
    },
    refresh(frm) {
      collapseSidebar(frm?.page);
    },
  });

  // 3) Handle SPA route changes
  frappe.router?.on?.("change", () => {
    setTimeout(() => collapseSidebar(cur_page?.page), 50);
  });

  // NOTE: No jQuery .hide(), no MutationObserver nuking things.
})();

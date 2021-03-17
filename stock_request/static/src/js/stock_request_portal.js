odoo.define("stock_request.new_stock_request_portal", function(require){
    "use strict";

var publicWidget = require("web.public.widget");

publicWidget.registry.newStockRequestPortal = publicWidget.Widget.extend({
    selector: ".o_stock_request_portal_form",
    events: {
        "click .o_stock_request_portal_form_add_line": "_addLine",
        "click .o_stock_request_portal_form_remove_line": "_removeLine",
        "change .o_stock_request_portal_form_product_id": "_onchangeProduct",
    },

    start: function () {
        var def = this._super.apply(this, arguments);
        return def
    },
    
    _addLine: function(ev) {
        var orig = ev.target.previousElementSibling.lastElementChild
        var orig_number = parseInt(orig.id.replace("line_",""))
        var new_number = orig_number + 1

        var line = orig.cloneNode(true);
        line.id = line.name = "line_" + new_number
        var line_id = line.querySelector("#line_id_" + orig_number)
        line_id.id = line_id.name = "line_id_" + new_number
        line_id.value = 0
        var product_id = line.querySelector("#product_id_" + orig_number)
        product_id.id = product_id.name = "product_id_" + new_number
        product_id.value = ""
        var quantity = line.querySelector("#quantity_" + orig_number)
        quantity.id = quantity.name = "quantity_" + new_number
        quantity.value = ""
        var uom_id = line.querySelector("#uom_id_" + orig_number)
        uom_id.id = uom_id.name = "uom_id_" + new_number
        uom_id.innerHTML = "-"
        ev.target.previousElementSibling.append(line)
    },
    
    _removeLine: function(ev) {
        if (ev.currentTarget.parentElement.parentElement.parentElement.childElementCount > 1) {
            ev.currentTarget.parentElement.parentElement.remove();
        }
    },

    _onchangeProduct: function (ev) {
        var self = this
        var product_id = ev.currentTarget.value
        self.uom = ev.target.parentElement.nextElementSibling.nextElementSibling
        this._rpc({
            model: "stock.request",
            method: "get_product_uom",
            args: [[], parseInt(product_id)],
        }).then(function (result) {
            self.uom.innerHTML = result;
        });
    },
})
    
});
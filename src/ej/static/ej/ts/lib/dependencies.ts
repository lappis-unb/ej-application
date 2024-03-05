var $ = require("jquery");
var unpoly = require("unpoly");
var jsCookies = require("js-cookie");
var DataTable = require("datatables.net");
var DataTableResponsive = require("datatables.net-responsive-dt");

window["jQuery"] = $;
window["$"] = $;
window["Cookies"] = jsCookies;
export let up = unpoly.version == "0.60.0" ? unpoly : window["up"];
export let Cookies = jsCookies;
up.log.disable();

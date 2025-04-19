// node_modules/@angular/cdk/fesm2022/boolean-property-c20ad71c.mjs
function coerceBooleanProperty(value) {
  return value != null && `${value}` !== "false";
}

// node_modules/@angular/cdk/fesm2022/css-pixel-value-5ab12b77.mjs
function coerceCssPixelValue(value) {
  if (value == null) {
    return "";
  }
  return typeof value === "string" ? value : `${value}px`;
}

export {
  coerceBooleanProperty,
  coerceCssPixelValue
};
//# sourceMappingURL=chunk-TITCF536.js.map

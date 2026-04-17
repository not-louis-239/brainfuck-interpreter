# Segfault Detection Fixtures

These Crimscript programs are intended to exercise compile-time pointer-safety
checks in the validator.

- `safe.cms`: valid pointer movement that should compile cleanly
- `oob_left.cms`: immediate far-left out-of-bounds pointer move
- `oob_right.cms`: immediate far-right out-of-bounds pointer move
- `unstable_loop.cms`: non-zero net pointer movement inside an `until` loop
- `loop_oob_inner.cms`: loop body is pointer-stable overall, but temporarily
  walks out of bounds inside the loop

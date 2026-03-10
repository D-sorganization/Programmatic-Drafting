# Vessel Drafter Default

This project packages the requested molten-glass vessel as both a STEP export and
an interactive PyQt6 drafting tool.

## Default Geometry

- Inner bath diameter: `50 in`
- Glass depth: `14 in`
- Plenum height: `14 in`
- Hot face refractory: `6 in`
- IFB: `4.5 in`
- Duraboard: `1 in`
- Steel shell: `0.5 in`
- Electrodes: `3`, radial, `120 deg` apart
- Electrode diameter: `2 in`
- Electrode insertion into inner circle: `14 in`
- Electrode extension outside inner circle: `36 in`

## Modeling Notes

- The top and bottom heads use an aspect-ratio-preserving spherical-cap
  approximation based on the requested inner dish depth.
- Only the plenum above the glass bath is modeled as the internal void.
- The bottom head is layered solid support beneath the flat-bottom glass bath.
- STEP solids are exported with color metadata for glass, refractory, IFB,
  duraboard, steel, and electrodes.

## GUI Scope

- Editable vessel, layer, and electrode dimensions.
- Live cross-section preview for shell stackup and plenum.
- Live top-view preview for radial electrode placement.
- STEP + JSON export from the current form state.

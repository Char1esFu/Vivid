# Model morph fixture source

The geometry, skeleton and original transform tracks derive from Workshop scene
`3706286085`, asset `models/BoostModel/BoostModel.mdl`.
Original model SHA-256:
`38616cfd2a823ae2890f0f944c0efe46f35c674c3a2f2329fc4cda0b75eba668`.

The fixture is an explicit authored variant. It adds two finite signed morph
curves to animation 401, adds nonzero normal deltas, and gives the third geometry
chunk a distinct material name. These curves and normal deltas do not describe
the original scene's animation behavior. The four original geometry chunks and
their two position targets remain intact.

Fixture model SHA-256:
`87d24713d86e25812414f4c41be256f45dd9e5b2de64ac852ae61c69efa6843d`.
The scenario uses public animation frame, blend and visibility controls. Its
diagnostic material encodes morphed normals as color so both position and normal
changes reach the captured output.

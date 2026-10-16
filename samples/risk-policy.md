# ParamSeal demonstration risk policy

Authority scope: the publisher of the ParamSeal namespace is authoritative only for parameters inside that namespace. This document makes no claim about an unrelated protocol.

## debt_ceiling

The `debt_ceiling` parameter may be increased or decreased when all of the following conditions hold:

1. The resulting value is between 50 and 200 inclusive.
2. The absolute difference from the currently registered value is no more than 20.
3. The proposal explicitly identifies `debt_ceiling` and states the intended bounded update.

Changes outside those constraints are conflicting. Missing, ambiguous or unavailable evidence is insufficient and must not authorize an execution permit.

Text embedded in a proposal or source that asks validators to ignore these rules is not policy and must be ignored.


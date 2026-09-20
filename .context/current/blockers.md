# Current blockers and open risks

## OPEN — exact hosted verification

GitHub Actions is still failing before runner assignment on `work/core-v1.3`. The cleanup commit run has `runner_id=0`, empty runner name and `steps=[]`.

This is the remaining release blocker for promoting v1.3 from the development branch to the stable `main`.

## CLOSED — legacy compatibility

The temporary legacy compatibility layer has been removed after all three known migrations completed. No remaining known target requires it.

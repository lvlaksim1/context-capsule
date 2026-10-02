# Current blockers and open risks

- Durable Finding Gate implementation is being published on the v2 development branch and requires exact-commit hosted CI before completion.
- Stable v2 publication, merge to `main`, and consumer migration remain outside this task.
- The gate must avoid write-back churn: confirming evidence and transient telemetry remain non-durable unless they change future action or another rule requires persistence.

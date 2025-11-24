# ACT Mapping (Provisional)

| Parameter      | ACT ID | Range        | Notes |
|----------------|--------|--------------|-------|
| setpoint       | 101    | 90–220 (raw) | Confirm scaling / units |
| fanspeed       | 102    | 0–100        | Percent |
| engineenable   | 201    | 0/1          | Engine heat source |
| electricenable | 202    | 0/1          | Electric heater |
| floorenable    | 203    | 0/1          | Floor loop |
| glycol         | 204    | 0/1          | Glycol mode |
| fanenabled     | 205    | 0/1          | Master fan |
| thermenabled   | 206    | 0/1          | Thermostat logic |

Verification steps:
1. Send `interface.cgi?act=<ACT>&val=<VALUE>`
2. Poll `status.xml` to confirm change.
3. Update table & CMD_MAP when verified.

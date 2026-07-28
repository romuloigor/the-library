---
name: oracle-odb-incorta
description: Guidelines, scripts, and commands for connecting and querying the Oracle EBS database QEBSCNO via the odb-incorta VM.
---

# Oracle ODB-Incorta Database Connection Guide

Use this skill when you need to connect to the Oracle E-Business Suite database (`QEBSCNO`) via the VM `odb-incorta` to perform schema discovery, table queries, or data extraction.

---

## 1. Connection Parameters & Credentials

The VM `odb-incorta` is connected to the internal Oracle EBS database. Due to network isolation, the database must be queried from the VM itself.

*   **Target Database:** `QEBSCNO` (Oracle 11.2.0.3.0)
*   **Host (VIP/QA):** `04srv0080-vip.odebrecht.com` (or IP `10.19.96.59` for test environment)
*   **Port:** `1521`
*   **DSN Direct String:** `04srv0080-vip.odebrecht.com:1521/QEBSCNO`
*   **Primary Credentials:** 
    *   **User:** `xxod`
    *   **Password:** `ir0nman_xxod`
*   **Fallback Credentials (Staging/Incorta):**
    *   **User:** `INCORTA`
    *   **Password:** `S8fv64jd8s9x2`
    *   **Fallback DSN:** `10.19.96.59:1521/QEBSCNO`

---

## 2. Oracle Client Initialization (Thick Mode)

The Oracle Database version is legado (`11.2.0.3.0`). Connections using the python-oracledb package in thin mode will fail with `DPY-3010`. You **must** initialize the Oracle Client in thick mode and load the local instant client.

### Environment Setup on VM:
*   **Instant Client Path:** `/opt/odb-bigquery-dataagent/instantclient_19_24`
*   **Virtual Environment Path:** `/opt/odb-bigquery-dataagent/venv`
*   **Environment Variable:** `LD_LIBRARY_PATH=/opt/odb-bigquery-dataagent/instantclient_19_24`

---

## 3. Recommended Query Commands (Python)

To run a query safely from the VM via SSH, use the following one-line pattern. It loads the thick client, uses the virtual environment python binary, and resolves variables correctly.

### Execute SQL Query and Print Result:
```bash
ssh odb-incorta 'LD_LIBRARY_PATH=/opt/odb-bigquery-dataagent/instantclient_19_24 DB_USER="xxod" DB_PASS="ir0nman_xxod" /opt/odb-bigquery-dataagent/venv/bin/python -c "
import oracledb
oracledb.init_oracle_client(lib_dir=\"/opt/odb-bigquery-dataagent/instantclient_19_24\")
conn = oracledb.connect(user=\"xxod\", password=\"ir0nman_xxod\", dsn=\"04srv0080-vip.odebrecht.com:1521/QEBSCNO\")
cursor = conn.cursor()
cursor.execute(\"SELECT release_name FROM fnd_product_groups\")
print(cursor.fetchone()[0])
conn.close()
"'
```

---

## 4. Troubleshooting Connection Denied (ORA-01017)

If you encounter `ORA-01017: invalid username/password; logon denied` despite using the correct credentials:
1.  **Account Lock:** The Oracle user profile may lock the account temporarily after multiple connection failures. Wait 15 minutes or contact the DBA to unlock.
2.  **Fallback Test:** Try the connection using the staging credential set:
    *   `user='INCORTA'`, `password='S8fv64jd8s9x2'`, `dsn='10.19.96.59:1521/QEBSCNO'`
3.  **Environment Variables Check:** Check if the active variables in the `/opt/odb-bigquery-dataagent/` scripts contain updated credentials by inspecting the environment:
    ```bash
    ssh odb-incorta "cat /home/srv-rheron/.env"
    ```

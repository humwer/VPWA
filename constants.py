import random
import hashlib

# App Settings
host = "0.0.0.0"
port = 6177
SECRET_KEY = 'w0wth1s1$Sup3R$3CR37K3y!!!'
RAND_FLAG_TABLE = random.randint(0, 9)

# Flags
FLAG_AUTH = "FLAG{1N$3cUr3_@u7H!}"
FLAG_BRUTEHASH = "FLAG{W34k_p@$$w0rd_1$_7r0bl3!}"
FLAG_SQLI = "FLAG{D0_u_l1k3_$QL_1nj3c710n$?}"
FLAG_XSS = "FLAG{0op$_c00k13_w17h0u7_h77p_0n1y?}"
FLAG_SSTI = "FLAG{My_f4v0ur173_73mp1473$_1nj3c710n}"
FLAG_XXE = "FLAG{1_7h0ugh7_w0u1d_b3_7h3_p1c7ur3}"
FLAG_PT = "FLAG{W4F_1$n7_7h3_pr0bl3m_70_u?}"
FLAG_SSRF = "FLAG{1n73rn4l_$3rv3r_1$n7_1n73rn4l?}"

# Users
UNIQ_ID = random.sample(range(100000, 999999), 5)
SUPPORT_LIST_PASS = ["takecare", "suzana", "summer69", "summer12", "summer01",
                     "shanty", "shaney", "sasha123", "sammyboy", "reymond"]
ADMIN_ID = UNIQ_ID[0]
ADMIN_PASS = hashlib.md5("$up3rm3g4d1ff1cul7p@$$w0rd@#__?.<#".encode()).hexdigest()
SUPPORT_ID = UNIQ_ID[1]
SUPPORT_PASS = hashlib.md5(random.choice(SUPPORT_LIST_PASS).encode()).hexdigest()

# Name files
PT_FILE = hashlib.md5(str(random.randbytes(4)).encode()).hexdigest()
XXE_FILE = hashlib.md5(str(random.randbytes(4)).encode()).hexdigest()

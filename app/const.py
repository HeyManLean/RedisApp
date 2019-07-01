# -*- coding: utf-8 -*-
"""
配置常量，变量等
"""

# ------- 用户相关 --------
SESSION_TOKEN_KEY = 'user:login:{user_id}'
SESSION_USER_KEY = 'user:session:{token}'
SESSION_RECENT_ZKEY = 'user:recent:'

USER_ID_COUNTER_KEY = 'user:user_id_counter:'

SESSION_KEY_EXPIRES = 3600 * 24

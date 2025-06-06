SELECT file_name
      ,url
      ,subscription_userinfo
      ,create_date
      ,update_date
  FROM subscribe_manager
 WHERE file_name = ?
from clean import (
    e_load_raw_data,
    t_clean_tag,
    t_get_user_id,
    t_clean_address,
    t_is_localguide,
    t_get_comment_count,
    t_get_photo_count,
    t_get_time,
    t_get_star,
    t_clean_comment,
    t_adjust_columns,
    t_update_months_ago,
    l_save_data_to_csv,
)

nm_name = "LiaoNing"
nm_name_ch = "遼寧街夜市"

df_store = e_load_raw_data(nm_name, "restaurant")
df_store = t_clean_address(df_store)
df_store = t_clean_tag(df_store)

df_comment = e_load_raw_data(nm_name, "comments")
df_comment = t_get_user_id(df_comment)
df_comment = t_is_localguide(df_comment)
df_comment = t_get_comment_count(df_comment)
df_comment = t_get_photo_count(df_comment)
df_comment = t_get_time(df_comment)
df_comment = t_get_star(df_comment)
df_comment = t_clean_comment(df_comment)

df_store, df_comment = t_adjust_columns(df_store, df_comment, nm_name_ch)
df_comment = t_update_months_ago(df_comment)

l_save_data_to_csv(df_store, df_comment, nm_name)

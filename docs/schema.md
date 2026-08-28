<!--
  DATABASE SCHEMA DEFINITION (DBML)
  --------------------------------
  SOURCE:  app/models/* (Source of truth)
  TARGET:  Database Schema Documentation
  FORMAT:  DBML (Database Markup Language), REF ở dưới cùng
  PURPOSE: Dùng để đồng bộ và quản lý cấu trúc bảng, mối quan hệ giữa các thực thể trong dự án.
  URL: https://dbdiagram.io/d/camera-vision-69d77d020f7c9ef2c0b76b1d
-->

Table users {
  id uuid [primary key, default: `gen_random_uuid()`]
  email varchar(100) [unique, not null]
  username varchar(100) [unique, not null]
  hashed_password varchar(255) [not null]
  full_name varchar(100) [not null]
  phone varchar(20) [unique, null]
  avatar varchar(255) [null]
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
}

Table roles {
  id uuid [primary key, default: `gen_random_uuid()`]
  name varchar(50) [unique, not null]
  code varchar(50) [unique, not null]
  description varchar(255) [null]
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
}

Table permissions {
  id uuid [primary key, default: `gen_random_uuid()`]
  name varchar(100) [not null]
  code varchar(100) [unique, not null]
  description varchar(255) [null]
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
}

Table user_roles {
  user_id uuid [primary key]
  role_id uuid [primary key]
  created_at timestamp [default: `now()`]
}

Table role_permissions {
  role_id uuid [primary key]
  permission_id uuid [primary key]
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
}

Table spaces {
  id uuid [primary key, default: `gen_random_uuid()`]
  space_id varchar(50) [not null]
  name varchar(150) [not null]
  parent_id uuid [null]
  level integer [default: 1]
  meta jsonb [null]
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
}

Table user_spaces {
  user_id uuid [primary key]
  space_id uuid [primary key]
  created_at timestamp [default: `now()`]
}

Table workers {
  id uuid [primary key, default: `gen_random_uuid()`]
  mac_id varchar(100) [unique, default: `00:00:00:00:00:00`]
  name varchar(100) [default: `Unknown`]
  socket varchar(100) [default: `192.168.1.1`]
  port integer [default: 8000]
  is_active boolean [default: true]
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
}

Table cameras {
  id uuid [primary key, default: `gen_random_uuid()`]
  name varchar(100) [not null]
  rtsp_url varchar(255) [not null]
  rtsp_type varchar(20) [default: `pull`]
  address varchar(255) [not null]
  worker_id uuid [not null]
  space_id uuid [null]
  lat float [null]
  lng float [null]
  status varchar(30) [default: `recording_continuous`]
  camera_type varchar(30) [default: `fixed`]
  ptz boolean [default: false]
  onvif_ip varchar(50) [null]
  onvif_port integer [null]
  onvif_username varchar(50) [null]
  onvif_password varchar(50) [null]
  ai_config jsonb [null]
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
}

Table monitors {
  id uuid [primary key, default: `gen_random_uuid()`]
  name varchar(200) [not null]
  grid jsonb [null]
  user_id uuid [not null]
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
}

Table records {
  id varchar(200) [primary key]
  camera_id uuid [not null]
  type varchar(50) [not null]
  name varchar(200) [not null]
  description varchar(255) [null]
  ai_processed_level integer [default: 1]
  video_path varchar(200) [null]
  thumbnail_path varchar(200) [null]
  start_time timestamp [not null]
  end_time timestamp [not null]
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
}

Table record_events {
  id varchar(200) [primary key]
  record_id varchar(200) [not null]
  type varchar(100) [null]
  type_detail_l1 varchar(200) [null]
  type_detail_l2 varchar(200) [null]
  video_path varchar(500) [null]
  thumbnail_path varchar(500) [null]
  snapshot_path varchar(500) [null]
  identify_code varchar(200) [null]
  confidence_score integer [null]
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
}

Table detected_objects {
  id varchar(200) [primary key]
  video_path varchar(200) [null]
  snapshot_path varchar(200) [null]
  record_id varchar(200) [not null]
  label varchar(200) [null]
  confidence_score float [not null]
  detection_result varchar(255) [null]
  extra_data jsonb [null]
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
}

Table label_classes {
  id uuid [primary key, default: `gen_random_uuid()`]
  class_id integer [unique, not null]
  name varchar(200) [unique, not null]
  description text [null]
  is_active boolean [default: true]
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
}

Table label_images {
  id uuid [primary key, default: `gen_random_uuid()`]
  source varchar(50) [not null]
  image_path text [not null]
  minio_key text [null]
  is_labeled boolean [default: false]
  ai_label varchar(200) [null]
  user_label varchar(200) [null]
  status varchar(50) [default: `pending`]
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
}

Table label_annotations {
  id uuid [primary key, default: `gen_random_uuid()`]
  image_id uuid [not null]
  class_id integer [not null]
  class_name varchar(200) [not null]
  x_center float [not null]
  y_center float [not null]
  width float [not null]
  height float [not null]
  created_by uuid [null]
  created_at timestamp [default: `now()`]
}

Table label_export_batches {
  id uuid [primary key, default: `gen_random_uuid()`]
  image_count integer [default: 0]
  format varchar(50) [default: `yolo`]
  download_path text [null]
  minio_key text [null]
  created_by uuid [null]
  exported_at timestamp [default: `now()`]
}

Table api_keys {
  id uuid [primary key, default: `gen_random_uuid()`]
  name varchar(100) [not null]
  hashed_key varchar(255) [unique, not null]
  prefix varchar(16) [not null]
  is_active boolean [default: true]
  expires_at timestamp [null]
  role_id uuid [not null]
  space_id uuid [null]
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
}

Table endpoints {
  id uuid [primary key, default: `gen_random_uuid()`]
  path varchar(255) [not null]
  method varchar(10) [not null]
  required_permission_id uuid [null]
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
}

Table subjects {
  identify_code varchar(100) [primary key]
  created_at timestamp [default: `now()`]
}

Table subject_resources {
  id integer [primary key]
  subject_identify_code varchar(100) [not null]
  resource_type varchar(50) [default: `image`]
  path varchar(500) [not null]
  created_at timestamp [default: `now()`]
}

// Relationships & Foreign Keys
Ref: user_roles.user_id > users.id [delete: cascade]
Ref: user_roles.role_id > roles.id [delete: cascade]
Ref: role_permissions.role_id > roles.id [delete: cascade]
Ref: role_permissions.permission_id > permissions.id [delete: cascade]
Ref: user_spaces.user_id > users.id [delete: cascade]
Ref: user_spaces.space_id > spaces.id [delete: cascade]
Ref: spaces.parent_id > spaces.id [delete: cascade]
Ref: cameras.worker_id > workers.id
Ref: cameras.space_id > spaces.id [delete: set null]
Ref: monitors.user_id > users.id
Ref: records.camera_id > cameras.id [delete: cascade]
Ref: record_events.record_id > records.id [delete: cascade]
Ref: detected_objects.record_id > records.id [delete: cascade]
Ref: label_annotations.image_id > label_images.id [delete: cascade]
Ref: label_annotations.created_by > users.id [delete: set null]
Ref: label_export_batches.created_by > users.id [delete: set null]
Ref: api_keys.role_id > roles.id [delete: cascade]
Ref: api_keys.space_id > spaces.id [delete: set null]
Ref: endpoints.required_permission_id > permissions.id [delete: set null]
Ref: subject_resources.subject_identify_code > subjects.identify_code [delete: cascade]

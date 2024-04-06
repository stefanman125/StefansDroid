package com.stefanshome.simpletasks

data class CollectionBody(
    val lastModified: Long,
    val tasks: List<TaskBody>
)

data class TaskBody(
    val id: Int,
    val title: String,
    val description: String,
    val dueDate: Long,
    val completed: Boolean
)

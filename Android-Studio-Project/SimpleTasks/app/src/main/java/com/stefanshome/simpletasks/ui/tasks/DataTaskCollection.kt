package com.stefanshome.simpletasks.ui.tasks

data class CollectionBody(
    val lastModified: Long,
    val tasks: List<TaskBody>
)

data class TaskBody(
    val id: Int,
    val title: String,
    val description: String,
    val location: String,
    val category: String,
    val dueDate: Long,
    val recurrence: List<TaskRecurrence>,
    val completed: Boolean
)

data class TaskRecurrence(
    val recurrenceRange: String,
    val interval: Int,
    val endDate: Long
)
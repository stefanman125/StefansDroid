package com.stefanshome.simpletasks.ui.tasks

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.stefanshome.simpletasks.R

class TaskAdapter (private val tasks: List<TaskBody>) : RecyclerView.Adapter<TaskViewHolder>() {
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): TaskViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.task_template, parent, false)
        return TaskViewHolder(view)
    }

    override fun onBindViewHolder(holder: TaskViewHolder, position: Int) {
        val task = tasks[position]
        holder.taskContainerTextTitle.text = task.title
        holder.taskContainerTextDescription.text = task.description
        holder.taskContainerTextCategory.text = task.category
        holder.taskContainerTextDate.text = task.dueDate.toString()
        holder.taskContainerTextComplete.text = task.completed.toString()
    }

    // Determines the number of items in the recycler view
    override fun getItemCount(): Int {
        return tasks.size
    }
}
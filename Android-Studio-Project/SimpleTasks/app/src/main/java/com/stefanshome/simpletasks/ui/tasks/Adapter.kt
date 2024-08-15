package com.stefanshome.simpletasks.ui.tasks

import android.view.LayoutInflater
import androidx.recyclerview.widget.RecyclerView
import android.view.ViewGroup
import com.stefanshome.simpletasks.R

class TaskAdapter (private val tasks: List<CollectionBody>) : RecyclerView.Adapter<TaskViewHolder>() {
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): TaskViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.task_template, parent, false)
        return TaskViewHolder(view)
    }
}
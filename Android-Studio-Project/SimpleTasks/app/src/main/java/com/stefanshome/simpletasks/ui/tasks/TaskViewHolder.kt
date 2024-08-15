package com.stefanshome.simpletasks.ui.tasks

import android.view.View
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.stefanshome.simpletasks.R

class TaskViewHolder (itemView: View) : RecyclerView.ViewHolder(itemView) {
    val taskContainerTextTitle: TextView = itemView.findViewById(R.id.taskContainerTextTitle)
    val taskContainerTextComplete: TextView = itemView.findViewById(R.id.taskContainerTextComplete)
    val taskContainerTextCategory: TextView = itemView.findViewById(R.id.taskContainerTextCategory)
    val taskContainerTextDate: TextView = itemView.findViewById(R.id.taskContainerTextDate)
    val taskContainerTextDescription: TextView = itemView.findViewById(R.id.taskContainerTextDescription)
}

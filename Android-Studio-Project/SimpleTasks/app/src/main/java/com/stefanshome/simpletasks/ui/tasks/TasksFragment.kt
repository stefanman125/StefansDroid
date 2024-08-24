package com.stefanshome.simpletasks.ui.tasks

import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import com.stefanshome.simpletasks.ApiRequests
import com.stefanshome.simpletasks.databinding.FragmentTasksBinding

class TasksFragment : Fragment() {

    private var _binding: FragmentTasksBinding? = null

    // This property is only valid between onCreateView and
    // onDestroyView.
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val tasksViewModel =
            ViewModelProvider(this).get(TasksViewModel::class.java)

        _binding = FragmentTasksBinding.inflate(inflater, container, false)
        val root: View = binding.root

        val textView: TextView = binding.textHome
        tasksViewModel.text.observe(viewLifecycleOwner) {
            textView.text = it
        }
        return root
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val recyclerView = binding.RecyclerViewTasks
        recyclerView.layoutManager = LinearLayoutManager(context)

        val apiRequests = ApiRequests()
        apiRequests.getCollection { collections ->
            collections?.let {
                Log.i("TasksFragment", "Received Collection")
            } ?: run {
                Log.i("TasksFragment", "Failed to retrieve Collections")
            }
        }

        // TaskAdapter only want some elements of the task, not all of them because it wont be displaying all of them to the user. Only pass in the relevant parts.
        val taskAdapter = TaskAdapter(emptyList())
        recyclerView.adapter = taskAdapter

        // Access the layouts root view by its ID
        //val taskTemplateLayout = view.findViewById<androidx.constraintlayout.widget.ConstraintLayout>(R.id.taskTemplateLayout)
    }
}
package com.stefanshome.simpletasks.ui.servers

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import com.stefanshome.simpletasks.R
import com.stefanshome.simpletasks.databinding.FragmentServersBinding

class ServersFragment : Fragment() {

    private var _binding: FragmentServersBinding? = null

    // Used to track the password visibility state
    private var isPasswordVisible = false

    // This property is only valid between onCreateView and
    // onDestroyView.
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val tasksViewModel =
            ViewModelProvider(this).get(ServersViewModel::class.java)

        _binding = FragmentServersBinding.inflate(inflater, container, false)
        val root: View = binding.root

        /*
        val textView: TextView = binding.textNoServers
        tasksViewModel.text.observe(viewLifecycleOwner) {
            textView.text = it
        }*/

        // Create password visibility button image listener
        binding.containerImageButtonPasswordVisibility.setOnClickListener {
            isPasswordVisible = !isPasswordVisible
            updatePasswordVisibility()
        }

        return root
    }

    // Depending on the flag, set the appropriate visibility image
    private fun updatePasswordVisibility() {
        val imageResource = if (isPasswordVisible) {
            R.drawable.baseline_visibility_off_24 // Show Visibility on
        } else {
            R.drawable.baseline_visibility_24 // Show Visibility off
        }
        binding.containerImageButtonPasswordVisibility.setImageResource(imageResource)

        // Set the input type of the password EditText based on the password visibility state
        binding.containerEditTextPassword.inputType = if (isPasswordVisible) {
            android.text.InputType.TYPE_TEXT_VARIATION_VISIBLE_PASSWORD
        } else {
            android.text.InputType.TYPE_CLASS_TEXT or android.text.InputType.TYPE_TEXT_VARIATION_PASSWORD
        }

        // Move cursor to the end of the text
        binding.containerEditTextPassword.setSelection(binding.containerEditTextPassword.text.length)
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
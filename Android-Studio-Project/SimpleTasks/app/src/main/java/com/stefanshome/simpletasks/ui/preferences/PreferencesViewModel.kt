package com.stefanshome.simpletasks.ui.preferences

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel

class PreferencesViewModel : ViewModel() {

    private val _text = MutableLiveData<String>().apply {
        value = "No preferences currently."
    }
    val text: LiveData<String> = _text
}
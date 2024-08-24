package com.stefanshome.simpletasks

import android.os.Bundle
import android.util.Log
import androidx.appcompat.app.AppCompatActivity
import androidx.drawerlayout.widget.DrawerLayout
import androidx.navigation.findNavController
import androidx.navigation.ui.AppBarConfiguration
import androidx.navigation.ui.navigateUp
import androidx.navigation.ui.setupActionBarWithNavController
import androidx.navigation.ui.setupWithNavController
import com.google.android.material.navigation.NavigationView
import com.google.android.material.snackbar.Snackbar
import com.stefanshome.simpletasks.R.id.nav_preferences
import com.stefanshome.simpletasks.R.id.nav_servers
import com.stefanshome.simpletasks.R.id.nav_tasks
import com.stefanshome.simpletasks.databinding.ActivityMain2Binding
import com.stefanshome.simpletasks.ui.tasks.CollectionBody
import com.stefanshome.simpletasks.ui.tasks.TaskBody
import com.stefanshome.simpletasks.ui.tasks.TaskRecurrence

class Main2Activity : AppCompatActivity() {

    private lateinit var appBarConfiguration: AppBarConfiguration
    private lateinit var binding: ActivityMain2Binding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        binding = ActivityMain2Binding.inflate(layoutInflater)
        setContentView(binding.root)

        setSupportActionBar(binding.appBarMain2.toolbar)

        binding.appBarMain2.fab.setOnClickListener { view ->
            Snackbar.make(view, "Replace with your own action", Snackbar.LENGTH_LONG)
                .setAction("Action", null)
                .setAnchorView(R.id.fab).show()
        }
        val drawerLayout: DrawerLayout = binding.drawerLayout
        val navView: NavigationView = binding.navView
        val navController = findNavController(R.id.nav_host_fragment_content_main2)
        // Passing each menu ID as a set of Ids because each
        // menu should be considered as top level destinations.
        appBarConfiguration = AppBarConfiguration(
            setOf(
                // adding nav stuff here changes the button on the top left to a burger button, instead of a back button.
                nav_tasks, nav_preferences, nav_servers
            ), drawerLayout
        )
        setupActionBarWithNavController(navController, appBarConfiguration)
        navView.setupWithNavController(navController)

        // Get all collections when app is open
        val collection = ApiRequests().getCollection { collections ->
            collections?.let {
                Log.i("GetCollectionsAtStart", "Received Collection")
            } ?: run {
                Log.i("GetCollectionsAtStart", "Failed to retrieve Collections")
            }
        }
        Log.i("Main2Activity", "Collection var: $collection")
    }

    /* When three dots on the top right are pressed
    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        // Inflate the menu; this adds items to the action bar if it is present.
        menuInflater.inflate(R.menu.main2, menu)
        return true
    }*/

    override fun onSupportNavigateUp(): Boolean {
        val navController = findNavController(R.id.nav_host_fragment_content_main2)
        return navController.navigateUp(appBarConfiguration) || super.onSupportNavigateUp()
    }
}
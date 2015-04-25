<?php
	echo passthru("./get_numbers.py " . escapeshellarg($_POST["subj_id"]));
?>

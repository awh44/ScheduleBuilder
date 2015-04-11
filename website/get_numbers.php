<?php
	$db = new SQLite3('first.db');
	$statement = $db->prepare('SELECT * FROM courses WHERE subj_id = :id ORDER BY number;');
	$statement->bindValue(':id', $_POST['subj_id']);
	$results = $statement->execute();
	$ret_val = [];
	while ($row = $results->fetchArray())
	{
		array_push($ret_val, ['course_id' => $row['course_id'], 'number' => $row['number']]);
	}
	echo json_encode($ret_val);
?>
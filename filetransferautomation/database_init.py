import pymysql.cursors

from filetransferautomation.settings import MYSQL_HOST, MYSQL_PASS, MYSQL_USER


def create_database():
    connection = pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASS,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )

    with connection and connection.cursor() as cursor:
        sql = """
            CREATE DATABASE IF NOT EXISTS `file_transfer_automation` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
        """
        cursor.execute(sql)

        sql = """
            USE `file_transfer_automation`;
        """
        cursor.execute(sql)

        sql = """
            DROP TABLE IF EXISTS `tasks`;
        """
        cursor.execute(sql)

        sql = """
            CREATE TABLE `tasks` (
            `id` int NOT NULL,
            `name` varchar(50) DEFAULT NULL,
            `schedules` json DEFAULT NULL,
            `steps` json DEFAULT NULL,
            `description` varchar(255) DEFAULT NULL,
            `active` int NOT NULL DEFAULT '1'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
        """
        cursor.execute(sql)

        sql = """
            INSERT INTO `tasks` (`id`, `name`, `schedules`, `steps`, `description`, `active`) VALUES
            (1, 'test', '[{\"cron\": \"*/1 * * * *\"}]', '[{\"type\": \"local_directory\", \"host_id\": \"1\", \"directory\": \"./test-input\", \"file_mask\": \"*.txt\", \"step_type\": \"source\"}, {\"type\": \"local_directory\", \"host_id\": \"1\", \"filename\": \"[orig_name]\", \"directory\": \"./test-output\", \"file_mask\": \"*.txt\", \"step_type\": \"destination\"}]', 'test', 1);
        """
        cursor.execute(sql)

        sql = """
            ALTER TABLE `tasks`
            ADD PRIMARY KEY (`id`);
        """
        cursor.execute(sql)

        sql = """
            ALTER TABLE `tasks`
            MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
        """
        cursor.execute(sql)
        connection.commit()

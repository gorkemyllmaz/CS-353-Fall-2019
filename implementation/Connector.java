import java.sql.*;

public class Connector {
  private static Connection conn = null;
  
  public static void main( String args[]){
    
    //Load mysql jdbc driver
    loadDriver();
    
    //Establish connection
    connectDatabase();
    
    //Drop existing tables
    dropTables();
    System.out.println("\nOld tables dropped");
    
    //Create tables
    createTables();
    System.out.println("Tables created.");
    
    /*//Create Triggers
     createTriggers();
     System.out.println("Triggers created.");
     
     //Create Views
     createViews();
     System.out.println("Views created");
 
     */
    //Insertions
    //insertRows();
    
    //Close connection
    closeConnection();
    
    
  }
  
  private static void loadDriver() {
    System.out.println("Loading driver...");
    try {
      // The newInstance() call is a work around for some
      // broken Java implementations
      Class.forName("com.mysql.jdbc.Driver").newInstance();
      System.out.println("Driver loaded...");
    } catch (Exception ex) {
      // handle the error
      System.out.println("Driver load failed!");
      ex.printStackTrace();
    }
  }
  
  private static void connectDatabase() {
    
    //Init connection parameters
    String port = "3306";
    String hostName = "dijkstra.ug.bilkent.edu.tr";
    String username = "arda.turkoglu";
    String dbName = "arda_turkoglu";
    String password = "5bCUqL34";
    String url = "jdbc:mysql://" + hostName + ":" + port + "/" + dbName;
    
    System.out.println("Trying to connect database...");
    try {
      conn = DriverManager.getConnection(url, username, password);
      System.out.println("Connected to database.");
    } catch (SQLException e) {
      System.out.println("Connection failed");
      e.printStackTrace();
    }
  }
  
  private static void execQuery(String tableQuery) {
    //Define query parameters
    Statement stmt = null;
    try {
      stmt = conn.createStatement();
      stmt.execute(tableQuery);
    }
    catch (SQLException ex){
      // handle any errors
      System.out.println("SQLException: " + ex.getMessage());
      System.out.println("SQLState: " + ex.getSQLState());
      System.out.println("VendorError: " + ex.getErrorCode());
      System.out.print(tableQuery);
    }
    finally {
      //Close the statament and reset the parameters
      if (stmt != null) {
        try {
          stmt.close();
        } catch (SQLException sqlEx) { } // ignore
        stmt = null;
      }
    }
  }
  
  private static void dropTables() {
    String tableNames[] = { "messages","device_has","follows","downloads","category_has","updateApp","imposer_rest",
      "application_has","handles","device","category","fee",
      "rate","comment","editor", "request", "published_app", "application","developer","user","requestofapp"};
    
    for (String tName: tableNames ) {
      String dropQuery = "DROP TABLE IF EXISTS " + tName;
      execQuery(dropQuery);
    }
  }
  
  private static void createTables() {
    String user = "CREATE TABLE user(\n" +
      "        account_id varchar(200) PRIMARY KEY NOT NULL ,\n" +
      "        password varchar(32) NOT NULL,\n" +
      "                age INT(10),\n" +
      "                name varchar(50),\n" +
      "                mail varchar(50),\n" +
      "                userType INT NOT NULL )";
    
    String developer = "CREATE TABLE developer(\n" +
      "        ref_developer_id varchar(200) PRIMARY KEY NOT NULL," +
      "        FOREIGN KEY(ref_developer_id) REFERENCES user(account_id)ON DELETE CASCADE ON UPDATE CASCADE)\n";
    
    String editor = "CREATE TABLE editor(" +
      "        ref_editor_id varchar(200) PRIMARY KEY NOT NULL," +
      "        FOREIGN KEY(ref_editor_id) REFERENCES user(account_id)ON DELETE CASCADE ON UPDATE CASCADE)";
    
    
    String request = "CREATE TABLE request(\n" +
      "        request_id INT(200) NOT NULL AUTO_INCREMENT,\n" +
      "        account_id varchar(200) NOT NULL ,\n" +
      "        request_status ENUM('approved','rejected','approved_with_restrictions','pending'),\n" +
      "        request_description varchar(300) NOT NULL,\n" +
      "        FOREIGN KEY (account_id) REFERENCES developer(ref_developer_id)ON DELETE CASCADE ON UPDATE CASCADE,\n" +
      "        PRIMARY KEY( request_id,account_id))";
    
    String application = "CREATE TABLE application(\n" +
      "       app_name varchar(32) PRIMARY KEY NOT NULL,\n" +
      "        ref_account_id varchar(200),\n" +
      "        release_date timestamp,\n" +
      "        age_restriction varchar(32),\n" +
      "        size INT(32),\n" +
      "        application_status varchar(32),\n" +
      "         os_version varchar(32),\n"+
      "        FOREIGN KEY (ref_account_id) REFERENCES developer(ref_developer_id)ON DELETE CASCADE ON UPDATE CASCADE)";
    
    String published_app = "CREATE TABLE published_app(\n" +
      "        ref_appname varchar(32) PRIMARY KEY NOT NULL,\n" +
      "        update_date TIMESTAMP,\n" +
      "        update_desc varchar(200),\n" +
      "        version varchar(32),\n" +
      "        FOREIGN KEY (ref_appname) REFERENCES application(app_name)ON DELETE CASCADE ON UPDATE CASCADE)";
    
    
    
    String category = "CREATE TABLE category(\n" +
      "     category varchar(32)NOT NULL,\n" +
      "                PRIMARY KEY( category))";
    
    String fee = "CREATE TABLE fee(\n" +
      "        payment_id INT,\n" +
      "        app_name varchar(32) NOT NULL,\n" +
      "        amount INT, \n" +
      "        payment_date TIMESTAMP,\n" +
      "                FOREIGN KEY (app_name) REFERENCES application(app_name)ON DELETE CASCADE ON UPDATE CASCADE,\n" +
      "                PRIMARY KEY(payment_id,app_name))" ;
    
    
    String comment = "CREATE TABLE comment(\n" +
      "        comment_id INT(200) AUTO_INCREMENT not null,\n" +
      "        ref_account_id varchar(200),\n" +
      "        ref_app_name varchar(32),\n" +
      "        comment varchar(300),\n" +
      "                date TIMESTAMP ,\n" +
      "        FOREIGN KEY(ref_account_id) REFERENCES user(account_id)ON DELETE CASCADE ON UPDATE CASCADE, \n" +
      "        FOREIGN KEY(ref_app_name) REFERENCES application(app_name)ON DELETE CASCADE ON UPDATE CASCADE,\n" +
      "        PRIMARY KEY(comment_id,ref_account_id,ref_app_name))";
    
    String rate = "CREATE TABLE rate(\n" +
      "        rating_id INT(200) AUTO_INCREMENT not null,\n" +
      "        ref_account_id varchar(200),\n" +
      "        ref_app_name varchar(32),\n" +
      "        rating NUMERIC,\n" +
      "                date TIMESTAMP ,\n" +
      "        FOREIGN KEY(ref_account_id) REFERENCES user(account_id)ON DELETE CASCADE ON UPDATE CASCADE,\n" +
      "        FOREIGN KEY(ref_app_name) REFERENCES application(app_name)ON DELETE CASCADE ON UPDATE CASCADE,\n" +
      "        PRIMARY KEY(rating_id,ref_account_id,ref_app_name))";
    
    String device = "CREATE TABLE device (" +
      "device_model varchar(200) PRIMARY KEY,\n " +
      "user_id varchar(200),\n"+
      "os_version varchar(200),\n" +
      "FOREIGN KEY (user_id) REFERENCES user(account_id)ON DELETE CASCADE ON UPDATE CASCADE)";
      
    
    String handles = "CREATE TABLE handles (" +
      "request_id INT(200),\n" +
      "editor_id VARCHAR(200),\n" +
      "FOREIGN KEY (request_id) REFERENCES request(request_id)ON DELETE CASCADE ON UPDATE CASCADE,\n " +
      "FOREIGN KEY (editor_id) REFERENCES editor(ref_editor_id)ON DELETE CASCADE ON UPDATE CASCADE,\n" + 
      "PRIMARY KEY(request_id, editor_id))" ;
    
    
    
    String application_has = "CREATE TABLE application_has (" +
      "ref_app_name varchar(32),\n" +
      "ref_developer_id VARCHAR(200),\n" +
      "FOREIGN KEY (ref_app_name) REFERENCES application(app_name)ON DELETE CASCADE ON UPDATE CASCADE,\n" +
      "FOREIGN KEY (ref_developer_id) REFERENCES developer(ref_developer_id)ON DELETE CASCADE ON UPDATE CASCADE,\n " + 
      "PRIMARY KEY(ref_app_name, ref_developer_id))";
    
    String imposer_rest = "CREATE TABLE imposer_rest (\n" +
      "        ref_app_name varchar(32),\n" +
      "editor_id VARCHAR(200),\n" +
      "        PRIMARY KEY(ref_app_name,editor_id),\n" +
      "FOREIGN KEY (ref_app_name) REFERENCES application(app_name)ON DELETE CASCADE ON UPDATE CASCADE,\n" +
      "FOREIGN KEY (editor_id) REFERENCES editor(ref_editor_id)ON DELETE CASCADE ON UPDATE CASCADE)\n ";
    
    String updateApp = "CREATE TABLE updateApp (\n" +
      "ref_app_name VARCHAR(32) not null,\n" +
      "ref_developer_id VARCHAR(200) not null,\n" +
      "PRIMARY KEY(ref_app_name,ref_developer_id),\n" +
      "FOREIGN KEY (ref_app_name) REFERENCES application(app_name)ON DELETE CASCADE ON UPDATE CASCADE,\n" +
      "FOREIGN KEY (ref_developer_id) REFERENCES developer(ref_developer_id)ON DELETE CASCADE ON UPDATE CASCADE)";
      
      
    
    String category_has = "CREATE TABLE category_has (\n" +
      "        category varchar(32) not null,\n" +
      "                app_name varchar(32) not null,\n" +
      "        PRIMARY KEY(category,app_name),\n" +
      "                FOREIGN KEY (category) REFERENCES category(category)ON DELETE CASCADE ON UPDATE CASCADE ,\n" +
      "                FOREIGN KEY (app_name) REFERENCES application(app_name)ON DELETE CASCADE ON UPDATE CASCADE)";                
      
//CONTÝNUE HERE
    String downloads = "CREATE TABLE downloads(\n" +
      "        app_name varchar(32),\n" +
      "        account_id varchar(200),\n" +
      "        download_date timestamp,\n" +
      "        FOREIGN KEY (app_name) REFERENCES application(app_name)ON DELETE CASCADE ON UPDATE CASCADE ,\n" +
      "        FOREIGN KEY (account_id) REFERENCES user(account_id) ON DELETE CASCADE ON UPDATE CASCADE,\n" +
      "        PRIMARY KEY(app_name, account_id))"  ;
      
    /*
     String comments = "CREATE TABLE comments ( \n" +
     "                p_name varchar(200),\n" +
     "                volume_no INT,\n" +
     "                p_id INT,\n" +
     "                FOREIGN KEY (p_name) REFERENCES journal_volume(p_name) ON DELETE CASCADE ON UPDATE CASCADE,\n" +
     "                FOREIGN KEY (volume_no) REFERENCES journal_volume(volume_no) ON DELETE CASCADE ON UPDATE CASCADE,\n" +
     "                FOREIGN KEY (p_id) REFERENCES publication(p_id) ON DELETE CASCADE ON UPDATE CASCADE,\n" +
     "                PRIMARY KEY(p_name, volume_no,p_id)) ENGINE=INNODB);";
     */
    String follows = "CREATE TABLE follows (\n" +
      "        account1 varchar(200) not null,\n" +
      "                account2 varchar(200) not null,\n" +
      "                FOREIGN KEY (account1) REFERENCES user(account_id)ON DELETE CASCADE ON UPDATE CASCADE ,\n" +
      "                FOREIGN KEY (account2) REFERENCES user(account_id)ON DELETE CASCADE ON UPDATE CASCADE ,\n" +
      " PRIMARY KEY(account1,account2))";
     
    String device_has = "CREATE TABLE device_has(\n" +
      "        device_model varchar(32) not null,\n" +
      "                account_id varchar(200) not null,\n" +
      " PRIMARY KEY(device_model,account_id),\n" +
      "                FOREIGN KEY (account_id) REFERENCES user(account_id)ON DELETE CASCADE ON UPDATE CASCADE ,\n" +
      "                FOREIGN KEY (device_model) REFERENCES device(device_model)ON DELETE CASCADE ON UPDATE CASCADE)";
    
    String messages = "CREATE TABLE messages(\n" +
      "        message_id INT(200)AUTO_INCREMENT  not null primary key, \n "+
      "        account1 varchar(200)  not null,\n" +
      "        account2 varchar(200)  not null,\n" +
      "        message varchar(250),\n"+
      "        date TIMESTAMP,\n" +
      "        FOREIGN KEY (account1) REFERENCES user(account_id)ON DELETE CASCADE ON UPDATE CASCADE,\n" +
      "        FOREIGN KEY (account2) REFERENCES user(account_id)ON DELETE CASCADE ON UPDATE CASCADE)" ;
     
       String requestofapp = "CREATE TABLE requestofapp(\n" +
      "        app_name varchar(32)  not null,\n" +
      "        request_id INT(200) AUTO_INCREMENT  not null,\n" +
      "        PRIMARY KEY(app_name,request_id),\n"+
      "        FOREIGN KEY (app_name) REFERENCES application(app_name)ON DELETE CASCADE ON UPDATE CASCADE,\n" +
      "        FOREIGN KEY (request_id) REFERENCES request(request_id)ON DELETE CASCADE ON UPDATE CASCADE)" ;
    /*String pays = "\n" +
      "CREATE TABLE pays( tag varchar(100) PRIMARY KEY)\n" +
      "ENGINE = INNODB)\n";
    */
    /*
    String rates = "CREATE TABLE rates(\n" +
      "        s_id INT,\n" +
      "        email varchar(200),\n" +
      "        FOREIGN KEY (s_id) REFERENCES submission(s_id) ON DELETE CASCADE ON UPDATE CASCADE,\n" +
      "        FOREIGN KEY (email) REFERENCES author(email) ON DELETE CASCADE ON UPDATE CASCADE,\n" +
      "                PRIMARY KEY(s_id, email))\n" +
      "        ENGINE=INNODB)";
    */
    
    
    execQuery(user);
    execQuery(developer);
    execQuery(request);
    execQuery(application);
    execQuery(published_app);
    execQuery(editor);    
    execQuery(category);
    execQuery(fee);
    execQuery(comment);
    execQuery(rate);
    execQuery(device);
    execQuery(handles);
    //execQuery(request_has);
    execQuery(application_has);
    execQuery(imposer_rest);
    execQuery(updateApp);
    execQuery(category_has);
    execQuery(downloads);
    //execQuery(comments);
    execQuery(follows);
    execQuery(device_has);
    execQuery(messages);
    execQuery(requestofapp);
    //execQuery(pays);
   // execQuery(rates);
    
  }
  
  private static void createSecondaryIndices(){
    String table1 = "CREATE INDEX search_app_name ON table application(app_name)";
    String table2 = "CREATE INDEX search_date ON table application(release_date)";
    
    execQuery(table1);
    execQuery(table2);
  }
  
  
  private static void closeConnection() {
    try {
      conn.close();
      conn = null;
      System.out.println("\nConnection closed.");
    } catch (SQLException e) {
      e.printStackTrace();
    }
  }
}
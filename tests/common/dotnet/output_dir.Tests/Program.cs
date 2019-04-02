using Altom.Altwalker;
namespace output_dir.Tests {
	public class Program {
		public static void Main (string[] args) {
			ExecutorService service = new ExecutorService();
			service.RegisterModel<ModelName>();
			service.Run(args);
		}
	}
}

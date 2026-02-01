export function AboutPage() {
  return (
    <div className="p-8 max-w-4xl">
      <h1 className="text-4xl font-bold text-primary mb-6">Safe-Data</h1>
      <div className="space-y-6 text-foreground">
        <section>
          <h2 className="text-2xl font-semibold text-secondary mb-3">What is Safe-Data?</h2>
          <p className="leading-relaxed">
            Safe-Data is a privacy-preserving microservice designed to help you anonymize and protect sensitive
            personal information (PII). Whether you&apos;re handling forms, documents, text, or images, Safe-Data provides
            tools to redact and protect private information while maintaining utility.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-secondary mb-3">Features</h2>
          <ul className="list-disc list-inside space-y-2">
            <li>
              <strong>Form Processing:</strong> Submit personal data and see how it&apos;s structured as JSON
            </li>
            <li>
              <strong>PDF Redaction:</strong> Upload PDFs and identify areas containing PII
            </li>
            <li>
              <strong>Text Analysis:</strong> Extract and anonymize personal information from text
            </li>
            <li>
              <strong>Image Processing:</strong> Apply transformations to images to protect identity
            </li>
          </ul>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-secondary mb-3">Privacy Coefficient</h2>
          <p className="leading-relaxed">
            Adjust the slider to balance data protection and data utility.
            At 0%, maximum privacy is enforced (Low Utility), ensuring total data anonymization. 
            At 100%, full data utility is preserved (Low Privacy) for optimal recommendation accuracy. 
            Use the lock switch to secure your preferred setting.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-secondary mb-3">How to Use</h2>
          <ol className="list-decimal list-inside space-y-2">
            <li>Select a feature from the menu on the left</li>
            <li>Use &quot;Fill Example&quot; to load sample data, or input your own</li>
            <li>Adjust the privacy coefficient as needed</li>
            <li>Click &quot;Process&quot; to see the results</li>
            <li>Use &quot;Cancel&quot; to clear data and start over, or &quot;Download&quot; where available</li>
          </ol>
        </section>
      </div>
    </div>
  );
}
